from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Sequence

from sqlalchemy import text
from sqlalchemy.orm import Session

from cockroach_continuity.embeddings import vector_literal
from cockroach_continuity.models import MemoryAssertion, RetrievalTrace


@dataclass(frozen=True)
class RetrievedAssertion:
    assertion_id: uuid.UUID
    kind: str
    statement: str
    distance: float


@dataclass(frozen=True)
class RetrievalResult:
    trace_id: uuid.UUID
    assertions: tuple[RetrievedAssertion, ...]


def store_assertion_embedding(
    session: Session, *, assertion_id: uuid.UUID, embedding: Sequence[float]
) -> None:
    assertion = session.get(MemoryAssertion, assertion_id)
    if assertion is None:
        raise LookupError("assertion not found")
    session.execute(
        text(
            "UPDATE memory_assertions "
            "SET embedding = CAST(:embedding AS VECTOR(1024)) "
            "WHERE id = :assertion_id"
        ),
        {"embedding": vector_literal(embedding), "assertion_id": assertion_id},
    )
    session.commit()


def store_event_embedding(
    session: Session, *, event_id: uuid.UUID, embedding: Sequence[float]
) -> None:
    result = session.execute(
        text(
            "UPDATE project_events "
            "SET embedding = CAST(:embedding AS VECTOR(1024)) "
            "WHERE id = :event_id"
        ),
        {"embedding": vector_literal(embedding), "event_id": event_id},
    )
    if result.rowcount != 1:
        session.rollback()
        raise LookupError("project event not found")
    session.commit()


def retrieve_approved_assertions(
    session: Session,
    *,
    project_id: uuid.UUID,
    query_text: str,
    query_embedding: Sequence[float],
    limit: int = 8,
    policy_version: str = "hackathon-v1",
) -> RetrievalResult:
    if not 1 <= limit <= 50:
        raise ValueError("retrieval limit must be between 1 and 50")
    normalized_query = query_text.strip()
    if not normalized_query:
        raise ValueError("retrieval query must not be empty")

    query_vector = vector_literal(query_embedding)
    rows = session.execute(
        text(
            "SELECT id, kind, statement, "
            "embedding <-> CAST(:query_vector AS VECTOR(1024)) AS distance "
            "FROM memory_assertions "
            "WHERE project_id = :project_id "
            "AND lifecycle = 'approved' "
            "AND embedding IS NOT NULL "
            "ORDER BY embedding <-> CAST(:query_vector AS VECTOR(1024)) "
            "LIMIT :limit"
        ),
        {
            "project_id": project_id,
            "query_vector": query_vector,
            "limit": limit,
        },
    ).mappings()

    assertions = tuple(
        RetrievedAssertion(
            assertion_id=uuid.UUID(str(row["id"])),
            kind=str(row["kind"]),
            statement=str(row["statement"]),
            distance=float(row["distance"]),
        )
        for row in rows
    )
    trace = RetrievalTrace(
        project_id=project_id,
        policy_version=policy_version,
        trigger="continuity_resume",
        query_text=normalized_query,
        selected_evidence=[
            {
                "assertion_id": str(item.assertion_id),
                "kind": item.kind,
                "distance": item.distance,
            }
            for item in assertions
        ],
        excluded_evidence=[],
        metadata_json={
            "scope_filter": {"project_id": str(project_id)},
            "lifecycle_filter": ["approved"],
            "distance_metric": "l2",
            "limit": limit,
        },
    )
    session.add(trace)
    session.commit()
    session.refresh(trace)
    return RetrievalResult(trace_id=trace.id, assertions=assertions)
