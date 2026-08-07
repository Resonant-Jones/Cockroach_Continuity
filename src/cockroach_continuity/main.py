from __future__ import annotations

from fastapi import FastAPI, Response, status

from cockroach_continuity.api import router as api_router
from cockroach_continuity.config import get_settings
from cockroach_continuity.db import database_ready

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(api_router)


@app.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.get("/health/ready")
def ready(response: Response) -> dict[str, str | bool]:
    ready_state = database_ready()
    if settings.database_required and not ready_state:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "ready" if ready_state else "degraded",
        "database": ready_state,
        "environment": settings.environment,
    }
