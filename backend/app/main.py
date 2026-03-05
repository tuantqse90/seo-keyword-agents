from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import update

from app.database import async_session
from app.models.report import Report, ReportStatus
from app.routers import projects, keywords, competitor, content, audit, workflows, reports, schedules, auth
from app.services.scheduler_service import start_scheduler, stop_scheduler


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {"status": "ok"}
