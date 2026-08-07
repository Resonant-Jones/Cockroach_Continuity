from __future__ import annotations

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from cockroach_continuity.approvals import CandidateDecisionResult, decide_candidate
from cockroach_continuity.candidates import CandidateProposal, persist_candidate_proposals
from cockroach_continuity.config import get_settings
from cockroach_continuity.embeddings import EMBEDDING_DIMENSION
from cockroach_continuity.ledger import append_project_event, create_project
from cockroach_continuity.models import (
    EvidenceLink,
    ExecutionAttempt,
    MemoryAssertion,
    MemoryCandidate,
    OperationReceipt,
    Project,
    ProjectEvent,
)
from cockroach_continuity.retrieval import (
    retrieve_approved_assertions,
    store_assertion_embedding,
    store_event_embedding,
)


def unit_vector(axis: int) -> list[float]:
    vector = [0.0] * EMBEDDING_DIMENSION
    vector[axis] = 1.0
    return vector


def create_approved_decision(
    session: Session,
    *,
    project_name: str,
    event_content: str,
    statement: str,
    event_key: str,
    decision_key: str,
) -> tuple[Project, ProjectEvent, CandidateDecisionResult]:
    project = create_project(session, name=project_name)
    event_result = append_project_event(
        session,
        project_id=project.id,
        content=event_content,
        idempotency_key=event_key,
    )
    event = session.get(ProjectEvent, event_result.event_id)
    assert event is not None
    candidate = persist_candidate_proposals(
        session,
        event=event,
        attempt_id=event_result.attempt_id,
        proposals=(CandidateProposal(kind="decision", statement=statement, confidence=0.99),),
    )[0]
    approval = decide_candidate(
        session,
        candidate_id=candidate.id,
        decision="approve",
        actor_ref="ci-user",
        idempotency_key=decision_key,
    )
    assert approval.assertion_id is not None
    return project, event, approval


def main() -> None:
    engine = create_engine(get_settings().database_url)
    with Session(engine) as session:
        project = create_project(session, name="CI Continuity Proof")

        first = append_project_event(
            session,
            project_id=project.id,
            content=(
                "Use CockroachDB as canonical continuity storage. "
                "Do not reopen the rejected split-store design."
            ),
            idempotency_key="ci-proof-event-1",
        )
        duplicate = append_project_event(
            session,
            project_id=project.id,
            content=(
                "Use CockroachDB as canonical continuity storage. "
                "Do not reopen the rejected split-store design."
            ),
            idempotency_key="ci-proof-event-1",
        )

        assert first.duplicate is False
        assert duplicate.duplicate is True
        assert duplicate.event_id == first.event_id
        assert duplicate.attempt_id == first.attempt_id
        assert duplicate.receipt_id == first.receipt_id

        event_count = session.scalar(
            select(func.count()).select_from(ProjectEvent).where(ProjectEvent.project_id == project.id)
        )
        attempt_count = session.scalar(
            select(func.count())
            .select_from(ExecutionAttempt)
            .join(ProjectEvent, ExecutionAttempt.project_event_id == ProjectEvent.id)
            .where(ProjectEvent.project_id == project.id)
        )
        assert event_count == 1
        assert attempt_count == 1

        try:
            append_project_event(
                session,
                project_id=project.id,
                content="Different intent must not reuse the same receipt.",
                idempotency_key="ci-proof-event-1",
            )
        except ValueError as exc:
            assert "different event content" in str(exc)
        else:
            raise AssertionError("idempotency key reuse with different content was accepted")

        event = session.get(ProjectEvent, first.event_id)
        assert event is not None
        candidates = persist_candidate_proposals(
            session,
            event=event,
            attempt_id=first.attempt_id,
            proposals=(
                CandidateProposal(
                    kind="decision",
                    statement="CockroachDB is the canonical continuity store.",
                    confidence=0.99,
                ),
                CandidateProposal(
                    kind="rejected_path",
                    statement="Split canonical approval state into a second datastore.",
                    confidence=0.95,
                ),
            ),
        )
        assert len(candidates) == 2
        assert all(candidate.status == "pending" for candidate in candidates)

        approved = decide_candidate(
            session,
            candidate_id=candidates[0].id,
            decision="approve",
            actor_ref="ci-user",
            idempotency_key="ci-approve-1",
        )
        approved_duplicate = decide_candidate(
            session,
            candidate_id=candidates[0].id,
            decision="approve",
            actor_ref="ci-user",
            idempotency_key="ci-approve-1",
        )
        rejected = decide_candidate(
            session,
            candidate_id=candidates[1].id,
            decision="reject",
            actor_ref="ci-user",
            idempotency_key="ci-reject-1",
        )

        assert approved.assertion_id is not None
        assert approved.duplicate is False
        assert approved_duplicate.duplicate is True
        assert approved_duplicate.assertion_id == approved.assertion_id
        assert rejected.assertion_id is None

        approved_candidate = session.get(MemoryCandidate, candidates[0].id)
        rejected_candidate = session.get(MemoryCandidate, candidates[1].id)
        assert approved_candidate is not None and approved_candidate.status == "approved"
        assert rejected_candidate is not None and rejected_candidate.status == "rejected"

        assertion_count = session.scalar(
            select(func.count())
            .select_from(MemoryAssertion)
            .where(MemoryAssertion.project_id == project.id)
        )
        assertion_evidence_count = session.scalar(
            select(func.count())
            .select_from(EvidenceLink)
            .where(
                EvidenceLink.target_type == "memory_assertion",
                EvidenceLink.target_id == approved.assertion_id,
            )
        )
        receipt_count = session.scalar(
            select(func.count())
            .select_from(OperationReceipt)
            .where(OperationReceipt.project_id == project.id)
        )

        assert assertion_count == 1
        assert assertion_evidence_count == 1
        assert receipt_count == 3

        canonical_vector = unit_vector(0)
        store_event_embedding(session, event_id=first.event_id, embedding=canonical_vector)
        store_assertion_embedding(
            session, assertion_id=approved.assertion_id, embedding=canonical_vector
        )

        other_project, other_event, other_approval = create_approved_decision(
            session,
            project_name="Isolation Control Project",
            event_content="A different project happens to contain semantically identical language.",
            statement="CockroachDB is the canonical continuity store.",
            event_key="ci-other-event",
            decision_key="ci-other-approve",
        )
        assert other_approval.assertion_id is not None
        store_event_embedding(session, event_id=other_event.id, embedding=canonical_vector)
        store_assertion_embedding(
            session,
            assertion_id=other_approval.assertion_id,
            embedding=canonical_vector,
        )

        retrieval = retrieve_approved_assertions(
            session,
            project_id=project.id,
            query_text="Where does canonical continuity live?",
            query_embedding=canonical_vector,
            limit=8,
        )
        assert [item.assertion_id for item in retrieval.assertions] == [approved.assertion_id]
        assert all(item.assertion_id != other_approval.assertion_id for item in retrieval.assertions)
        assert other_project.id != project.id

        print(
            "continuity vertical-slice proof passed:",
            {
                "project_id": str(project.id),
                "event_id": str(first.event_id),
                "attempt_id": str(first.attempt_id),
                "approved_assertion_id": str(approved.assertion_id),
                "rejected_candidate_id": str(rejected.candidate_id),
                "retrieval_trace_id": str(retrieval.trace_id),
            },
        )


if __name__ == "__main__":
    main()
