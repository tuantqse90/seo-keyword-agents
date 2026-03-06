import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import update, text
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings
from app.database import async_session, engine
from app.models.report import Report, ReportStatus
from app.routers import projects, keywords, competitor, content, audit, workflows, reports, schedules, auth
from app.services.scheduler_service import start_scheduler, stop_scheduler
from app.middleware.logging_middleware import setup_logging

# Setup structured logging
setup_logging()

# In-memory rate limit store: {ip: [timestamps]}
_rate_limits: dict[str, list[float]] = {}
RATE_LIMIT = 60  # requests per window
RATE_WINDOW = 60  # seconds


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: recover stuck streaming reports
    async with async_session() as db:
        await db.execute(
            update(Report)
            .where(Report.status == ReportStatus.STREAMING)
            .values(status=ReportStatus.FAILED, summary="Server restarted during analysis")
        )
        await db.commit()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="SEO Dashboard API", version="0.1.0", lifespan=lifespan)

# CORS middleware — origins configurable via CORS_ORIGINS env var
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Simple in-memory rate limiting per IP."""
    if request.url.path in ("/api/health", "/api/health/ready"):
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    now = time.time()

    if client_ip not in _rate_limits:
        _rate_limits[client_ip] = []
    _rate_limits[client_ip] = [t for t in _rate_limits[client_ip] if now - t < RATE_WINDOW]

    if len(_rate_limits[client_ip]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later."},
            headers={"Retry-After": str(RATE_WINDOW)},
        )

    _rate_limits[client_ip].append(now)

    logger = logging.getLogger("api")
    start = time.time()
    logger.info(f"{request.method} {request.url.path}")

    response = await call_next(request)

    duration = round((time.time() - start) * 1000, 1)
    logger.info(f"{request.method} {request.url.path} {response.status_code} {duration}ms")

    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(RATE_LIMIT - len(_rate_limits[client_ip]))
    return response


app.include_router(projects.router)
app.include_router(keywords.router)
app.include_router(competitor.router)
app.include_router(content.router)
app.include_router(audit.router)
app.include_router(workflows.router)
app.include_router(reports.router)
app.include_router(schedules.router)
app.include_router(auth.router)


@app.get("/api/health")
async def health():
    """Liveness check — is the server running?"""
    return {"status": "ok"}


@app.get("/api/health/ready")
async def health_ready():
    """Readiness check — can the server handle requests (DB connection OK)?"""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": str(e)},
        )
