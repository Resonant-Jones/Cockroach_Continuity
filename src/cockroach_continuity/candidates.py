from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Protocol

from sqlalchemy.orm import Session

from cockroach_continuity.models import EvidenceLink, MemoryCandidate, ProjectEvent

_CANDIDATE_KINDS = {
    "decision",
    "constraint",
    "correction",
    "open_loop",
    "rejected_path",
    "next_action",
}


@dataclass(frozen=True)
class CandidateProposal:
    kind: str
    statement: str
    confidence: float | None = None
    sensitivity: str = "project"


class CandidateExtractor(Protocol):
    def extract(self, *, event: ProjectEvent) -> tuple[CandidateProposal, ...]: ...


class BedrockCandidateExtractor:
    """Structured candidate extraction through a Bedrock Runtime Converse client.

    The client is injected so the domain layer does not create AWS sessions or own credentials.
    """

    tool_name = "propose_continuity_candidates"

    def __init__(self, *, client: Any, model_id: str) -> None:
        self._client = client
        self._model_id = model_id

    def extract(self, *, event: ProjectEvent) -> tuple[CandidateProposal, ...]:
        schema = {
            "type": "object",
            "properties": {
                "candidates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "kind": {"type": "string", "enum": sorted(_CANDIDATE_KINDS)},
                            "statement": {"type": "string"},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                            "sensitivity": {
                                "type": "string",
                                "enum": ["project", "private", "restricted"],
                            },
                        },
                        "required": ["kind", "statement", "sensitivity"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["candidates"],
            "additionalProperties": False,
        }
        response = self._client.converse(
            modelId=self._model_id,
            system=[
                {
                    "text": (
                        "Extract only project continuity candidates directly supported by the event. "
                        "Do not infer personal traits. Confidence is advisory and never grants approval."
                    )
                }
            ],
            messages=[{"role": "user", "content": [{"text": event.content}]}],
            toolConfig={
                "tools": [
                    {
                        "toolSpec": {
                            "name": self.tool_name,
                            "description": "Return project continuity candidates supported by the event.",
                            "inputSchema": {"json": schema},
                        }
                    }
                ],
                "toolChoice": {"tool": {"name": self.tool_name}},
            },
            inferenceConfig={"temperature": 0, "maxTokens": 1200},
        )

        content = response.get("output", {}).get("message", {}).get("content", [])
        for block in content:
            tool_use = block.get("toolUse") if isinstance(block, dict) else None
            if tool_use and tool_use.get("name") == self.tool_name:
                return _parse_proposals(tool_use.get("input", {}))
        raise RuntimeError("Bedrock response did not contain the required candidate tool call")


def _parse_proposals(payload: object) -> tuple[CandidateProposal, ...]:
    if not isinstance(payload, dict):
        raise ValueError("candidate payload must be an object")
    raw_candidates = payload.get("candidates", [])
    if not isinstance(raw_candidates, list):
        raise ValueError("candidates must be an array")

    proposals: list[CandidateProposal] = []
    for raw in raw_candidates:
        if not isinstance(raw, dict):
            raise ValueError("candidate must be an object")
        kind = str(raw.get("kind", ""))
        statement = str(raw.get("statement", "")).strip()
        sensitivity = str(raw.get("sensitivity", "project"))
        confidence_raw = raw.get("confidence")
        confidence = float(confidence_raw) if confidence_raw is not None else None
        if kind not in _CANDIDATE_KINDS:
            raise ValueError(f"unsupported candidate kind: {kind}")
        if not statement:
            raise ValueError("candidate statement must not be empty")
        if sensitivity not in {"project", "private", "restricted"}:
            raise ValueError(f"unsupported sensitivity: {sensitivity}")
        if confidence is not None and not 0 <= confidence <= 1:
            raise ValueError("candidate confidence must be between 0 and 1")
        proposals.append(
            CandidateProposal(
                kind=kind,
                statement=statement,
                confidence=confidence,
                sensitivity=sensitivity,
            )
        )
    return tuple(proposals)


def persist_candidate_proposals(
    session: Session,
    *,
    event: ProjectEvent,
    attempt_id: uuid.UUID,
    proposals: tuple[CandidateProposal, ...],
) -> tuple[MemoryCandidate, ...]:
    rows: list[MemoryCandidate] = []
    for proposal in proposals:
        candidate = MemoryCandidate(
            project_id=event.project_id,
            proposed_by_attempt_id=attempt_id,
            kind=proposal.kind,
            statement=proposal.statement,
            confidence=proposal.confidence,
            sensitivity=proposal.sensitivity,
            status="pending",
            source_excerpt_hashes=[event.content_hash],
        )
        session.add(candidate)
        session.flush()
        session.add(
            EvidenceLink(
                project_id=event.project_id,
                target_type="memory_candidate",
                target_id=candidate.id,
                source_type="project_event",
                source_id=event.id,
                relationship="proposed_from",
                source_hash=event.content_hash,
            )
        )
        rows.append(candidate)
    session.commit()
    return tuple(rows)
