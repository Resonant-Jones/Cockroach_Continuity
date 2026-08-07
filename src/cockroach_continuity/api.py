from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from cockroach_continuity.db import get_session
from cockroach_continuity.ledger import append_project_event, create_project

router = APIRouter(prefix="/api")


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


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def post_project(
    request: ProjectCreateRequest, session: Session = Depends(get_session)
) -> ProjectResponse:
    try:
        project = create_project(session, name=request.name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ProjectResponse(id=project.id, name=project.name, status=project.status)


@router.post("/projects/{project_id}/events", response_model=EventAppendResponse)
def post_project_event(
    project_id: uuid.UUID,
    request: EventAppendRequest,
    session: Session = Depends(get_session),
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
