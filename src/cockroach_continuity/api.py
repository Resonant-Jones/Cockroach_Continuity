from __future__ import annotations

import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from cockroach_continuity.approvals import decide_candidate
from cockroach_continuity.db import get_session
from cockroach_continuity.ledger import append_project_event, create_project
from cockroach_continuity.models import MemoryCandidate

router = APIRouter(prefix="/api")
SessionDep = Annotated[Session, Depends(get_session)]


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    status: str


class EventAppendRequest(BaseModel):
    content: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1, max_length=200)
    session_id: uuid.UUID | None = None
    event_kind: str = Field(default="user_update", min_length=1, max_length=64)


class EventAppendResponse(BaseModel):
    event_id: uuid.UUID
    attempt_id: uuid.UUID
    receipt_id: uuid.UUID
    duplicate: bool


class CandidateResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    kind: str
    statement: str
    confidence: float | None
    sensitivity: str
    status: str


class CandidateDecisionRequest(BaseModel):
    decision: Literal["approve", "reject", "revise", "defer"]
    actor_ref: str = Field(min_length=1, max_length=200)
    idempotency_key: str = Field(min_length=1, max_length=200)
    revised_statement: str | None = None


class CandidateDecisionResponse(BaseModel):
    candidate_id: uuid.UUID
    decision_id: uuid.UUID
    assertion_id: uuid.UUID | None
    receipt_id: uuid.UUID
    duplicate: bool


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def post_project(request: ProjectCreateRequest, session: SessionDep) -> ProjectResponse:
    try:
        project = create_project(session, name=request.name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ProjectResponse(id=project.id, name=project.name, status=project.status)


@router.post("/projects/{project_id}/events", response_model=EventAppendResponse)
def post_project_event(
    project_id: uuid.UUID,
    request: EventAppendRequest,
    session: SessionDep,
) -> EventAppendResponse:
    try:
        result = append_project_event(
            session,
            project_id=project_id,
            content=request.content,
            idempotency_key=request.idempotency_key,
            session_id=request.session_id,
            event_kind=request.event_kind,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return EventAppendResponse(
        event_id=result.event_id,
        attempt_id=result.attempt_id,
        receipt_id=result.receipt_id,
        duplicate=result.duplicate,
    )


@router.get("/projects/{project_id}/candidates", response_model=list[CandidateResponse])
def get_project_candidates(
    project_id: uuid.UUID,
    session: SessionDep,
    lifecycle: str = "pending",
) -> list[CandidateResponse]:
    candidates = session.scalars(
        select(MemoryCandidate)
        .where(MemoryCandidate.project_id == project_id, MemoryCandidate.status == lifecycle)
        .order_by(MemoryCandidate.created_at.asc())
    ).all()
    return [
        CandidateResponse(
            id=candidate.id,
            project_id=candidate.project_id,
            kind=candidate.kind,
            statement=candidate.statement,
            confidence=candidate.confidence,
            sensitivity=candidate.sensitivity,
            status=candidate.status,
        )
        for candidate in candidates
    ]


@router.post("/candidates/{candidate_id}/decision", response_model=CandidateDecisionResponse)
def post_candidate_decision(
    candidate_id: uuid.UUID,
    request: CandidateDecisionRequest,
    session: SessionDep,
) -> CandidateDecisionResponse:
    try:
        result = decide_candidate(
            session,
            candidate_id=candidate_id,
            decision=request.decision,
            actor_ref=request.actor_ref,
            idempotency_key=request.idempotency_key,
            revised_statement=request.revised_statement,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return CandidateDecisionResponse(
        candidate_id=result.candidate_id,
        decision_id=result.decision_id,
        assertion_id=result.assertion_id,
        receipt_id=result.receipt_id,
        duplicate=result.duplicate,
    )
