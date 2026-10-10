"""FastAPI application for the Nexora HQ dashboard and read-only registry API."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from .config import Settings
from .database import HQDatabase

logger = logging.getLogger("nexora_hq")


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    service: str
    database: Literal["ready", "unavailable"]
    venture_integrations: Literal["not_configured"]


class Venture(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    category: str
    description: str
    repository_url: str | None
    connection_state: Literal["not_connected", "connected", "degraded", "unavailable"]
    created_at: str
    updated_at: str


class VentureList(BaseModel):
    count: int = Field(ge=0)
    items: list[Venture]


class ActivityItem(BaseModel):
    id: int
    kind: str
    title: str
    detail: str
    source: str
    created_at: str


class ActivityList(BaseModel):
    count: int = Field(ge=0)
    items: list[ActivityItem]


def create_app(database_path: str | Path | None = None) -> FastAPI:
    settings = Settings.from_env()
    path = database_path or settings.database_path
    database = HQDatabase(path)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        database.initialize()
        yield
        database.close()

    application = FastAPI(
        title="Nexora HQ API",
        description="Parent-company venture registry and HQ-owned activity. Venture adapters are not enabled.",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.state.database = database

    @application.exception_handler(Exception)
    async def unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        # Log only the exception class; do not expose messages, paths, or request secrets.
        logger.error("Unhandled HQ API error type=%s", type(exc).__name__)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    @application.get("/api/health", response_model=HealthResponse, tags=["system"])
    def health(request: Request) -> HealthResponse | JSONResponse:
        database_ready = request.app.state.database.ping()
        if not database_ready:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "degraded",
                    "service": "nexora-hq",
                    "database": "unavailable",
                    "venture_integrations": "not_configured",
                },
            )
        return HealthResponse(
            status="ok",
            service="nexora-hq",
            database="ready",
            venture_integrations="not_configured",
        )

    @application.get("/api/ventures", response_model=VentureList, tags=["ventures"])
    def ventures(request: Request) -> VentureList:
        items = request.app.state.database.list_ventures()
        return VentureList(count=len(items), items=items)

    @application.get("/api/activity", response_model=ActivityList, tags=["activity"])
    def activity(
        request: Request,
        limit: Annotated[int, Query(ge=1, le=100)] = 50,
    ) -> ActivityList:
        items = request.app.state.database.list_activity(limit=limit)
        return ActivityList(count=len(items), items=items)

    static_dir = Path(__file__).resolve().parents[2] / "apps" / "web"
    if static_dir.is_dir():
        application.mount("/", StaticFiles(directory=static_dir, html=True), name="web")
    return application


app = create_app()
