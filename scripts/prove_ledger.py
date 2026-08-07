from __future__ import annotations

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from cockroach_continuity.config import get_settings
from cockroach_continuity.ledger import append_project_event, create_project
from cockroach_continuity.models import ExecutionAttempt, OperationReceipt, ProjectEvent


def main() -> None:
    engine = create_engine(get_settings().database_url)
    with Session(engine) as session:
        project = create_project(session, name="CI Continuity Proof")

        first = append_project_event(
            session,
            project_id=project.id,
            content="CockroachDB owns durable continuity truth.",
            idempotency_key="ci-proof-event-1",
        )
        duplicate = append_project_event(
            session,
            project_id=project.id,
            content="CockroachDB owns durable continuity truth.",
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
        receipt_count = session.scalar(
            select(func.count())
            .select_from(OperationReceipt)
            .where(OperationReceipt.project_id == project.id)
        )

        assert event_count == 1
        assert attempt_count == 1
        assert receipt_count == 1

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

        print(
            "ledger proof passed:",
            {
                "project_id": str(project.id),
                "event_id": str(first.event_id),
                "attempt_id": str(first.attempt_id),
                "receipt_id": str(first.receipt_id),
            },
        )


if __name__ == "__main__":
    main()
