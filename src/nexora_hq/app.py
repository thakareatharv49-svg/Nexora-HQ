"""FastAPI application for the Nexora HQ dashboard and read-only registry API."""
from __future__ import annotations

import hashlib
import hmac
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal
from urllib.parse import urlsplit

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

from .auth import create_session, verify_password, verify_session
from .config import Settings
from .database import HQDatabase

logger = logging.getLogger("nexora_hq")
LOGIN_FAILURE_LIMIT = 5
LOGIN_WINDOW_SECONDS = 15 * 60
LOGIN_LOCKOUT_SECONDS = 15 * 60


class AuthStatus(BaseModel):
    auth_required: bool
    authenticated: bool


class LoginRequest(BaseModel):
    password: str = Field(min_length=1, max_length=1024)


class VentureCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    category: str = Field(min_length=2, max_length=60)
    description: str = Field(min_length=10, max_length=500)
    repository_url: AnyHttpUrl | None = None


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

    production = settings.environment == "production"
    application = FastAPI(
        title="Nexora HQ API",
        description="Parent-company venture registry and HQ-owned activity. Venture adapters are not enabled.",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=None if production else "/docs",
        redoc_url=None if production else "/redoc",
        openapi_url=None if production else "/openapi.json",
    )
    application.state.database = database
    application.state.settings = settings

    def require_auth(request: Request) -> None:
        current_settings = request.app.state.settings
        if current_settings.admin_password_hash and not verify_session(
            request.cookies.get("nexora_session"), current_settings.session_secret or ""
        ):
            raise HTTPException(status_code=401, detail="Authentication required")

    def validate_same_origin(request: Request) -> None:
        origin = request.headers.get("origin")
        if origin and urlsplit(origin).netloc != request.headers.get("host"):
            raise HTTPException(status_code=403, detail="Cross-origin request rejected")

    @application.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/auth/"):
            response.headers.setdefault("Cache-Control", "no-store")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
            "base-uri 'self'; form-action 'self'; frame-ancestors 'none'",
        )
        return response

    @application.exception_handler(Exception)
    async def unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        # Log only the exception class; do not expose messages, paths, or request secrets.
        logger.error("Unhandled HQ API error type=%s", type(exc).__name__)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    @application.get("/api/auth/status", response_model=AuthStatus, tags=["authentication"])
    def auth_status(request: Request) -> AuthStatus:
        current_settings = request.app.state.settings
        auth_required = current_settings.admin_password_hash is not None
        authenticated = not auth_required or verify_session(
            request.cookies.get("nexora_session"), current_settings.session_secret or ""
        )
        return AuthStatus(auth_required=auth_required, authenticated=authenticated)

    @application.post("/api/auth/login", response_model=AuthStatus, tags=["authentication"])
    def login(payload: LoginRequest, request: Request, response: Response) -> AuthStatus:
        validate_same_origin(request)
        current_settings = request.app.state.settings
        password_hash = current_settings.admin_password_hash
        session_secret = current_settings.session_secret
        if not password_hash or not session_secret:
            raise HTTPException(status_code=409, detail="Authentication is not configured")
        client_host = request.client.host if request.client else "unknown"
        rate_limit_key = hmac.new(
            session_secret.encode(),
            f"nexora-login-rate-limit:{client_host}".encode(),
            hashlib.sha256,
        ).hexdigest()
        database = request.app.state.database
        retry_after = database.login_lockout_seconds(rate_limit_key)
        if retry_after:
            raise HTTPException(
                status_code=429,
                detail="Too many failed sign-in attempts. Try again later.",
                headers={"Retry-After": str(retry_after)},
            )
        if not verify_password(payload.password, password_hash):
            retry_after = database.record_login_failure(
                rate_limit_key,
                failure_limit=LOGIN_FAILURE_LIMIT,
                window_seconds=LOGIN_WINDOW_SECONDS,
                lockout_seconds=LOGIN_LOCKOUT_SECONDS,
            )
            logger.warning("Rejected administrator sign-in")
            if retry_after:
                raise HTTPException(
                    status_code=429,
                    detail="Too many failed sign-in attempts. Try again later.",
                    headers={"Retry-After": str(retry_after)},
                )
            raise HTTPException(status_code=401, detail="Invalid credentials")
        database.clear_login_failures(rate_limit_key)
        database.record_activity(
            "SECURITY", "Administrator signed in", "A valid administrator session was created.", "auth"
        )
        response.set_cookie(
            key="nexora_session",
            value=create_session(session_secret),
            max_age=8 * 60 * 60,
            path="/",
            secure=current_settings.environment == "production",
            httponly=True,
            samesite="strict",
        )
        response.headers["Cache-Control"] = "no-store"
        return AuthStatus(auth_required=True, authenticated=True)

    @application.post("/api/auth/logout", response_model=AuthStatus, tags=["authentication"])
    def logout(request: Request, response: Response) -> AuthStatus:
        validate_same_origin(request)
        current_settings = request.app.state.settings
        if current_settings.admin_password_hash and verify_session(
            request.cookies.get("nexora_session"), current_settings.session_secret or ""
        ):
            request.app.state.database.record_activity(
                "SECURITY", "Administrator signed out", "An administrator session was ended.", "auth"
            )
        response.delete_cookie(
            key="nexora_session",
            path="/",
            secure=current_settings.environment == "production",
            httponly=True,
            samesite="strict",
        )
        response.headers["Cache-Control"] = "no-store"
        return AuthStatus(
            auth_required=current_settings.admin_password_hash is not None,
            authenticated=current_settings.admin_password_hash is None,
        )

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

    @application.get(
        "/api/ventures", response_model=VentureList, tags=["ventures"], dependencies=[Depends(require_auth)]
    )
    def ventures(request: Request) -> VentureList:
        items = request.app.state.database.list_ventures()
        return VentureList(count=len(items), items=items)

    @application.post(
        "/api/ventures",
        response_model=Venture,
        status_code=201,
        tags=["ventures"],
        dependencies=[Depends(require_auth)],
    )
    def create_venture(payload: VentureCreate, request: Request) -> Venture:
        repository_url = (
            str(payload.repository_url) if payload.repository_url is not None else None
        )
        try:
            item = request.app.state.database.create_venture(
                name=payload.name,
                category=payload.category,
                description=payload.description,
                repository_url=repository_url,
            )
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        request.app.state.database.record_activity(
            "REGISTRY",
            f"Venture registered: {item['name']}",
            "A venture record was added to the HQ registry.",
            "hq",
        )
        return Venture.model_validate(item)

    @application.get(
        "/api/activity", response_model=ActivityList, tags=["activity"], dependencies=[Depends(require_auth)]
    )
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
