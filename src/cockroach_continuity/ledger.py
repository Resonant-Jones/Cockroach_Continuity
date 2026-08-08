from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from cockroach_continuity.models import ExecutionAttempt, OperationReceipt, Project, ProjectEvent


@dataclass(frozen=True)
class EventWriteResult:
    event_id: uuid.UUID
    attempt_id: uuid.UUID
    receipt_id: uuid.UUID
    duplicate: bool


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def create_project(session: Session, *, name: str, owner_ref: str = "demo-owner") -> Project:
    project = Project(name=name.strip(), owner_ref=owner_ref)
    if not project.name:
        raise ValueError("project name must not be empty")
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def _find_event_receipt(
    session: Session, *, project_id: uuid.UUID, idempotency_key: str
) -> OperationReceipt | None:
    statement = select(OperationReceipt).where(
        OperationReceipt.project_id == project_id,
        OperationReceipt.operation_kind == "append_project_event",
        OperationReceipt.idempotency_key == idempotency_key,
    )
    return session.scalar(statement)


def _result_from_receipt(receipt: OperationReceipt, *, expected_hash: str) -> EventWriteResult:
    stored_hash = str(receipt.result_json.get("content_hash", ""))
    if stored_hash != expected_hash:
        raise ValueError("idempotency key was already used for different event content")

    return EventWriteResult(
        event_id=uuid.UUID(str(receipt.result_json["event_id"])),
        attempt_id=uuid.UUID(str(receipt.result_json["attempt_id"])),
        receipt_id=receipt.id,
        duplicate=True,
    )


def append_project_event(
    session: Session,
    *,
    project_id: uuid.UUID,
    content: str,
    idempotency_key: str,
    session_id: uuid.UUID | None = None,
    event_kind: str = "user_update",
) -> EventWriteResult:
    normalized_content = content.strip()
    normalized_key = idempotency_key.strip()
    if not normalized_content:
        raise ValueError("event content must not be empty")
    if not normalized_key:
        raise ValueError("idempotency key must not be empty")

    project = session.get(Project, project_id)
    if project is None:
        raise LookupError("project not found")

    content_hash = _content_hash(normalized_content)
    existing = _find_event_receipt(
        session, project_id=project_id, idempotency_key=normalized_key
    )
    if existing is not None:
        return _result_from_receipt(existing, expected_hash=content_hash)

    event = ProjectEvent(
        project_id=project_id,
        session_id=session_id,
        event_kind=event_kind,
        content=normalized_content,
        content_hash=content_hash,
        source_type="native",
        authored_by="user",
    )
    attempt = ExecutionAttempt(
        project_event_id=event.id,
        attempt_number=1,
        status="queued",
    )
    receipt = OperationReceipt(
        project_id=project_id,
        operation_kind="append_project_event",
        idempotency_key=normalized_key,
        status="accepted",
        target_type="project_event",
        target_id=event.id,
        result_json={},
    )

    # UUID defaults are Python-side and materialize when the objects are inserted.
    session.add(event)
    session.flush()
    attempt.project_event_id = event.id
    session.add(attempt)
    session.flush()
    receipt.target_id = event.id
    receipt.result_json = {
        "event_id": str(event.id),
        "attempt_id": str(attempt.id),
        "content_hash": content_hash,
    }
    session.add(receipt)

    try:
        session.commit()
    except IntegrityError:
        # A concurrent equivalent request may have claimed the unique receipt first.
        session.rollback()
        winner = _find_event_receipt(
            session, project_id=project_id, idempotency_key=normalized_key
        )
        if winner is None:
            raise
        return _result_from_receipt(winner, expected_hash=content_hash)

    session.refresh(receipt)
    return EventWriteResult(
        event_id=event.id,
        attempt_id=attempt.id,
        receipt_id=receipt.id,
        duplicate=False,
    )
