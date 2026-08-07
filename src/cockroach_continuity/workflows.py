from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from cockroach_continuity.candidates import CandidateExtractor, persist_candidate_proposals
from cockroach_continuity.embeddings import EmbeddingProvider
from cockroach_continuity.models import ExecutionAttempt, MemoryCandidate, ProjectEvent
from cockroach_continuity.retrieval import store_event_embedding


class CandidateExtractionFailed(RuntimeError):
    pass


@dataclass(frozen=True)
class ExtractionWorkflowResult:
    event_id: uuid.UUID
    attempt_id: uuid.UUID
    candidate_ids: tuple[uuid.UUID, ...]
    duplicate: bool
    event_embedding_status: str


def _latest_attempt(session: Session, *, event_id: uuid.UUID) -> ExecutionAttempt | None:
    return session.scalar(
        select(ExecutionAttempt)
        .where(ExecutionAttempt.project_event_id == event_id)
        .order_by(ExecutionAttempt.attempt_number.desc())
        .limit(1)
    )


def _candidates_for_attempt(
    session: Session, *, attempt_id: uuid.UUID
) -> tuple[MemoryCandidate, ...]:
    return tuple(
        session.scalars(
            select(MemoryCandidate)
            .where(MemoryCandidate.proposed_by_attempt_id == attempt_id)
            .order_by(MemoryCandidate.created_at.asc())
        ).all()
    )


def extract_candidates_for_event(
    session: Session,
    *,
    event_id: uuid.UUID,
    extractor: CandidateExtractor,
    embedding_provider: EmbeddingProvider | None = None,
    provider_name: str = "bedrock",
    model_id: str | None = None,
) -> ExtractionWorkflowResult:
    event = session.get(ProjectEvent, event_id)
    if event is None:
        raise LookupError("project event not found")

    latest = _latest_attempt(session, event_id=event_id)
    if latest is not None and latest.status == "completed":
        existing = _candidates_for_attempt(session, attempt_id=latest.id)
        return ExtractionWorkflowResult(
            event_id=event.id,
            attempt_id=latest.id,
            candidate_ids=tuple(candidate.id for candidate in existing),
            duplicate=True,
            event_embedding_status="unknown",
        )
    if latest is not None and latest.status == "running":
        raise ValueError("candidate extraction is already running")

    if latest is None:
        attempt = ExecutionAttempt(
            project_event_id=event.id,
            attempt_number=1,
            status="queued",
        )
        session.add(attempt)
        session.flush()
    elif latest.status == "queued":
        attempt = latest
    elif latest.status in {"retryable_failed", "fatal_failed", "cancelled"}:
        attempt = ExecutionAttempt(
            project_event_id=event.id,
            attempt_number=latest.attempt_number + 1,
            status="queued",
        )
        session.add(attempt)
        session.flush()
    else:
        raise ValueError(f"unsupported attempt state: {latest.status}")

    attempt.status = "running"
    attempt.provider = provider_name
    attempt.model = model_id
    attempt.error_code = None
    attempt.error_detail = None
    session.commit()

    try:
        proposals = extractor.extract(event=event)
    except Exception as exc:
        session.refresh(attempt)
        attempt.status = "retryable_failed"
        attempt.error_code = type(exc).__name__[:100]
        attempt.error_detail = str(exc)[:4000]
        session.commit()
        raise CandidateExtractionFailed(str(exc)) from exc

    candidates = persist_candidate_proposals(
        session,
        event=event,
        attempt_id=attempt.id,
        proposals=proposals,
    )

    embedding_status = "not_requested"
    if embedding_provider is not None:
        try:
            embedding = embedding_provider.embed(event.content)
            store_event_embedding(session, event_id=event.id, embedding=embedding)
            embedding_status = "stored"
        except Exception:
            # Event and candidate writes are already durable. Embedding is derived state.
            session.rollback()
            embedding_status = "failed"

    session.refresh(attempt)
    attempt.status = "completed"
    session.commit()

    return ExtractionWorkflowResult(
        event_id=event.id,
        attempt_id=attempt.id,
        candidate_ids=tuple(candidate.id for candidate in candidates),
        duplicate=False,
        event_embedding_status=embedding_status,
    )
