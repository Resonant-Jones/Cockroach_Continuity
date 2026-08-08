from __future__ import annotations

import uuid
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from cockroach_continuity.approvals import decide_candidate
from cockroach_continuity.compiler import compile_continuity_snapshot
from cockroach_continuity.config import get_settings
from cockroach_continuity.db import get_session
from cockroach_continuity.ledger import append_project_event, create_project
from cockroach_continuity.models import MemoryAssertion, MemoryCandidate
from cockroach_continuity.providers import build_candidate_extractor, build_embedding_provider
from cockroach_continuity.retrieval import retrieve_approved_assertions, store_assertion_embedding
from cockroach_continuity.workflows import CandidateExtractionFailed, extract_candidates_for_event

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


class ExtractionResponse(BaseModel):
    event_id: uuid.UUID
    attempt_id: uuid.UUID
    candidate_ids: list[uuid.UUID]
    duplicate: bool
    event_embedding_status: str


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
    assertion_embedding_status: str


class ContinuityRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    limit: int = Field(default=8, ge=1, le=50)


class ContinuityResponse(BaseModel):
    snapshot_id: uuid.UUID
    retrieval_trace_id: uuid.UUID
    input_hash: str
    brief: dict[str, Any]


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


@router.post("/events/{event_id}/extract", response_model=ExtractionResponse)
def post_event_extraction(event_id: uuid.UUID, session: SessionDep) -> ExtractionResponse:
    settings = get_settings()
    try:
        result = extract_candidates_for_event(
            session,
            event_id=event_id,
            extractor=build_candidate_extractor(settings),
            embedding_provider=build_embedding_provider(settings),
            provider_name="bedrock",
            model_id=settings.candidate_model_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except CandidateExtractionFailed as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return ExtractionResponse(
        event_id=result.event_id,
        attempt_id=result.attempt_id,
        candidate_ids=list(result.candidate_ids),
        duplicate=result.duplicate,
        event_embedding_status=result.event_embedding_status,
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

    embedding_status = "not_applicable"
    if result.assertion_id is not None:
        assertion = session.get(MemoryAssertion, result.assertion_id)
        if assertion is None:
            embedding_status = "failed"
        else:
            try:
                embedding = build_embedding_provider().embed(assertion.statement)
                store_assertion_embedding(
                    session,
                    assertion_id=assertion.id,
                    embedding=embedding,
                )
                embedding_status = "stored"
            except Exception:
                session.rollback()
                embedding_status = "failed"

    return CandidateDecisionResponse(
        candidate_id=result.candidate_id,
        decision_id=result.decision_id,
        assertion_id=result.assertion_id,
        receipt_id=result.receipt_id,
        duplicate=result.duplicate,
        assertion_embedding_status=embedding_status,
    )


@router.post("/projects/{project_id}/continuity", response_model=ContinuityResponse)
def post_continuity(
    project_id: uuid.UUID,
    request: ContinuityRequest,
    session: SessionDep,
) -> ContinuityResponse:
    try:
        query_embedding = build_embedding_provider().embed(request.query)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"embedding provider failed: {exc}",
        ) from exc

    retrieval = retrieve_approved_assertions(
        session,
        project_id=project_id,
        query_text=request.query,
        query_embedding=query_embedding,
        limit=request.limit,
    )
    compiled = compile_continuity_snapshot(
        session,
        project_id=project_id,
        retrieval=retrieval,
    )
    return ContinuityResponse(
        snapshot_id=compiled.snapshot_id,
        retrieval_trace_id=compiled.retrieval_trace_id,
        input_hash=compiled.input_hash,
        brief=compiled.brief,
    )
