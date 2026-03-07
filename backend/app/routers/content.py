import asyncio
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, async_session
from app.models.report import Report, ReportStatus
from app.schemas.report import AnalyzeRequest, AnalyzeResponse, ReportOut
from app.schemas.content import ContentReportOut, ContentBriefOut
from app.services.content_service import create_content_report, save_content_results, get_content_report
from app.services.keyword_service import mark_report_failed
from app.services.claude_client import stream_claude_response
from app.services.prompt_builder import build_content_prompt
from app.services.auth_service import require_auth
from app.services.stream_manager import create_stream, get_stream, remove_stream
from app.services.webhook_service import notify_report_completed, notify_report_failed
from app.models.user import User

router = APIRouter(prefix="/api/content", tags=["content"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_content(req: AnalyzeRequest, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    report = await create_content_report(db, req.query, req.project_id)
    report_id = str(report.id)
    create_stream(report_id)
    asyncio.create_task(_run_analysis(report_id, req.query))
    return AnalyzeResponse(report_id=report.id, stream_url=f"/api/content/stream/{report_id}")


async def _run_analysis(report_id: str, query: str):
    queue = get_stream(report_id)
    full_text = ""
    try:
        async with async_session() as db:
            report = await db.get(Report, uuid.UUID(report_id))
            if report:
                report.status = ReportStatus.STREAMING
                await db.commit()

        prompt = build_content_prompt(query)
        async for chunk in stream_claude_response(prompt):
            full_text += chunk
            await queue.put({"event": "chunk", "data": chunk})

        async with async_session() as db:
            await save_content_results(db, uuid.UUID(report_id), full_text)
        await queue.put({"event": "done", "data": report_id})
        await notify_report_completed("content", query, report_id)
    except Exception as e:
        async with async_session() as db:
            await mark_report_failed(db, uuid.UUID(report_id), str(e))
        await queue.put({"event": "error", "data": str(e)})
        await notify_report_failed("content", query, str(e))
    finally:
        await queue.put(None)


@router.get("/stream/{report_id}")
async def stream_content(report_id: str):
    queue = get_stream(report_id)
    if not queue:
        raise HTTPException(404, "Stream not found")

    async def event_generator():
        try:
            while True:
                msg = await queue.get()
                if msg is None:
                    break
                yield msg
        finally:
            remove_stream(report_id)

    return EventSourceResponse(event_generator())


@router.get("/{report_id}", response_model=ContentReportOut)
async def get_content(report_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    report = await get_content_report(db, report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    brief = report.content_briefs[0] if report.content_briefs else None
    return ContentReportOut(
        report=ReportOut.model_validate(report),
        content_brief=ContentBriefOut.model_validate(brief) if brief else None,
    )
