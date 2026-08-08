from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from cockroach_continuity.models import (
    ApprovalDecision,
    EvidenceLink,
    MemoryAssertion,
    MemoryCandidate,
    OperationReceipt,
)


@dataclass(frozen=True)
class CandidateDecisionResult:
    candidate_id: uuid.UUID
    decision_id: uuid.UUID
    assertion_id: uuid.UUID | None
    receipt_id: uuid.UUID
    duplicate: bool


def _intent_hash(*, decision: str, revised_statement: str | None) -> str:
    payload = f"{decision}\n{(revised_statement or '').strip()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _existing_receipt(
    session: Session, *, project_id: uuid.UUID, idempotency_key: str
) -> OperationReceipt | None:
    return session.scalar(
        select(OperationReceipt).where(
            OperationReceipt.project_id == project_id,
            OperationReceipt.operation_kind == "candidate_decision",
            OperationReceipt.idempotency_key == idempotency_key,
        )
    )


def _result_from_receipt(
    receipt: OperationReceipt, *, candidate_id: uuid.UUID, expected_intent_hash: str
) -> CandidateDecisionResult:
    payload = receipt.result_json
    if str(payload.get("candidate_id", "")) != str(candidate_id):
        raise ValueError("idempotency key was already used for a different candidate")
    if str(payload.get("intent_hash", "")) != expected_intent_hash:
        raise ValueError("idempotency key was already used for a different decision")

    assertion_raw = payload.get("assertion_id")
    return CandidateDecisionResult(
        candidate_id=candidate_id,
        decision_id=uuid.UUID(str(payload["decision_id"])),
        assertion_id=uuid.UUID(str(assertion_raw)) if assertion_raw else None,
        receipt_id=receipt.id,
        duplicate=True,
    )


def _next_assertion_version(
    session: Session, *, project_id: uuid.UUID, logical_key: str
) -> int:
    current = session.scalar(
        select(func.max(MemoryAssertion.version)).where(
            MemoryAssertion.project_id == project_id,
            MemoryAssertion.logical_key == logical_key,
        )
    )
    return int(current or 0) + 1


def decide_candidate(
    session: Session,
    *,
    candidate_id: uuid.UUID,
    decision: str,
    actor_ref: str,
    idempotency_key: str,
    revised_statement: str | None = None,
    actor_kind: str = "user",
) -> CandidateDecisionResult:
    normalized_decision = decision.strip().lower()
    normalized_actor = actor_ref.strip()
    normalized_key = idempotency_key.strip()
    revised = revised_statement.strip() if revised_statement else None

    if actor_kind != "user":
        raise PermissionError("only a user actor may govern durable continuity")
    if normalized_decision not in {"approve", "reject", "revise", "defer"}:
        raise ValueError("decision must be approve, reject, revise, or defer")
    if normalized_decision == "revise" and not revised:
        raise ValueError("revise requires revised_statement")
    if not normalized_actor:
        raise ValueError("actor_ref must not be empty")
    if not normalized_key:
        raise ValueError("idempotency key must not be empty")

    candidate = session.scalar(
        select(MemoryCandidate).where(MemoryCandidate.id == candidate_id).with_for_update()
    )
    if candidate is None:
        raise LookupError("candidate not found")

    project_id = candidate.project_id
    intent_hash = _intent_hash(decision=normalized_decision, revised_statement=revised)
    existing = _existing_receipt(
        session, project_id=project_id, idempotency_key=normalized_key
    )
    if existing is not None:
        return _result_from_receipt(
            existing, candidate_id=candidate.id, expected_intent_hash=intent_hash
        )

    if candidate.status != "pending":
        raise ValueError(f"candidate is not pending: {candidate.status}")

    source_links: list[EvidenceLink] = []
    if normalized_decision in {"approve", "revise"}:
        source_links = list(
            session.scalars(
                select(EvidenceLink).where(
                    EvidenceLink.target_type == "memory_candidate",
                    EvidenceLink.target_id == candidate.id,
                )
            ).all()
        )
        if not source_links:
            raise ValueError("candidate has no evidence links and cannot be promoted")

    assertion: MemoryAssertion | None = None
    if normalized_decision in {"approve", "revise"}:
        logical_key = f"candidate:{candidate.id}"
        statement = revised if normalized_decision == "revise" else candidate.statement
        assert statement is not None
        assertion = MemoryAssertion(
            project_id=project_id,
            candidate_id=candidate.id,
            logical_key=logical_key,
            version=_next_assertion_version(
                session, project_id=project_id, logical_key=logical_key
            ),
            kind=candidate.kind,
            statement=statement,
            lifecycle="approved",
            sensitivity=candidate.sensitivity,
        )
        session.add(assertion)
        session.flush()

        for link in source_links:
            session.add(
                EvidenceLink(
                    project_id=project_id,
                    target_type="memory_assertion",
                    target_id=assertion.id,
                    source_type=link.source_type,
                    source_id=link.source_id,
                    relationship="supported_by",
                    source_hash=link.source_hash,
                )
            )

    decision_row = ApprovalDecision(
        project_id=project_id,
        candidate_id=candidate.id,
        assertion_id=assertion.id if assertion else None,
        actor_ref=normalized_actor,
        decision=normalized_decision,
        revised_statement=revised,
    )
    session.add(decision_row)
    session.flush()

    candidate.status = {
        "approve": "approved",
        "reject": "rejected",
        "revise": "revised",
        "defer": "pending",
    }[normalized_decision]

    receipt = OperationReceipt(
        project_id=project_id,
        operation_kind="candidate_decision",
        idempotency_key=normalized_key,
        status="completed",
        target_type="memory_candidate",
        target_id=candidate.id,
        result_json={
            "candidate_id": str(candidate.id),
            "decision_id": str(decision_row.id),
            "assertion_id": str(assertion.id) if assertion else None,
            "intent_hash": intent_hash,
        },
    )
    session.add(receipt)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        winner = _existing_receipt(
            session, project_id=project_id, idempotency_key=normalized_key
        )
        if winner is None:
            raise
        return _result_from_receipt(
            winner, candidate_id=candidate.id, expected_intent_hash=intent_hash
        )

    session.refresh(receipt)
    return CandidateDecisionResult(
        candidate_id=candidate.id,
        decision_id=decision_row.id,
        assertion_id=assertion.id if assertion else None,
        receipt_id=receipt.id,
        duplicate=False,
    )
