from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from cockroach_continuity.models import (
    ContinuitySnapshot,
    EvidenceLink,
    MemoryAssertion,
    ProjectEvent,
)
from cockroach_continuity.retrieval import RetrievalResult


@dataclass(frozen=True)
class CompiledContinuity:
    snapshot_id: uuid.UUID
    retrieval_trace_id: uuid.UUID
    brief: dict[str, Any]
    input_hash: str


def _input_hash(*, policy_version: str, assertions: list[MemoryAssertion]) -> str:
    payload = {
        "policy_version": policy_version,
        "assertions": [
            {"id": str(assertion.id), "version": assertion.version}
            for assertion in assertions
        ],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def compile_continuity_snapshot(
    session: Session,
    *,
    project_id: uuid.UUID,
    retrieval: RetrievalResult,
    policy_version: str = "hackathon-v1",
) -> CompiledContinuity:
    assertions: list[MemoryAssertion] = []
    evidence_by_assertion: dict[str, list[dict[str, Any]]] = {}

    for retrieved in retrieval.assertions:
        assertion = session.get(MemoryAssertion, retrieved.assertion_id)
        if assertion is None:
            raise LookupError(f"retrieved assertion not found: {retrieved.assertion_id}")
        if assertion.project_id != project_id:
            raise ValueError("retrieval result crossed the requested project boundary")
        if assertion.lifecycle != "approved":
            raise ValueError(f"ineligible assertion lifecycle: {assertion.lifecycle}")
        assertions.append(assertion)

        links = session.scalars(
            select(EvidenceLink).where(
                EvidenceLink.target_type == "memory_assertion",
                EvidenceLink.target_id == assertion.id,
            )
        ).all()
        if not links:
            raise ValueError(f"assertion has no evidence: {assertion.id}")

        evidence_rows: list[dict[str, Any]] = []
        for link in links:
            if link.source_type != "project_event":
                evidence_rows.append(
                    {
                        "source_type": link.source_type,
                        "source_id": str(link.source_id),
                        "source_hash": link.source_hash,
                    }
                )
                continue
            event = session.get(ProjectEvent, link.source_id)
            if event is None:
                raise ValueError(f"source event missing: {link.source_id}")
            if event.project_id != project_id:
                raise ValueError("assertion evidence crossed the project boundary")
            evidence_rows.append(
                {
                    "source_type": "project_event",
                    "source_id": str(event.id),
                    "source_hash": link.source_hash or event.content_hash,
                    "event_kind": event.event_kind,
                    "content": event.content,
                    "occurred_at": event.occurred_at.isoformat(),
                }
            )
        evidence_by_assertion[str(assertion.id)] = evidence_rows

    categories: dict[str, list[dict[str, Any]]] = {
        "decisions": [],
        "constraints": [],
        "corrections": [],
        "open_loops": [],
        "rejected_paths": [],
        "next_actions": [],
    }
    kind_to_category = {
        "decision": "decisions",
        "constraint": "constraints",
        "correction": "corrections",
        "open_loop": "open_loops",
        "rejected_path": "rejected_paths",
        "next_action": "next_actions",
    }

    for assertion in assertions:
        category = kind_to_category.get(assertion.kind)
        if category is None:
            raise ValueError(f"unsupported assertion kind: {assertion.kind}")
        categories[category].append(
            {
                "assertion_id": str(assertion.id),
                "version": assertion.version,
                "statement": assertion.statement,
                "evidence": evidence_by_assertion[str(assertion.id)],
            }
        )

    digest = _input_hash(policy_version=policy_version, assertions=assertions)
    brief: dict[str, Any] = {
        "project_id": str(project_id),
        "policy_version": policy_version,
        "retrieval_trace_id": str(retrieval.trace_id),
        "summary": {
            "selected_assertions": len(assertions),
            "evidence_events": sum(len(rows) for rows in evidence_by_assertion.values()),
        },
        **categories,
    }

    session.execute(
        update(ContinuitySnapshot)
        .where(
            ContinuitySnapshot.project_id == project_id,
            ContinuitySnapshot.status == "active",
        )
        .values(status="stale")
    )
    snapshot = ContinuitySnapshot(
        project_id=project_id,
        retrieval_trace_id=retrieval.trace_id,
        policy_version=policy_version,
        status="active",
        snapshot_json=brief,
        source_assertion_versions=[
            {"assertion_id": str(assertion.id), "version": assertion.version}
            for assertion in assertions
        ],
        input_hash=digest,
        freshness_boundary=f"policy:{policy_version};input:{digest}",
    )
    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)

    return CompiledContinuity(
        snapshot_id=snapshot.id,
        retrieval_trace_id=retrieval.trace_id,
        brief=brief,
        input_hash=digest,
    )
