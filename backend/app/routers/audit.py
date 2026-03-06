import asyncio
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, async_session
from app.models.report import Report, ReportStatus
from app.schemas.report import AnalyzeRequest, AnalyzeResponse, ReportOut
from app.schemas.audit import AuditReportOut, AuditResultOut
from app.services.audit_service import create_audit_report, save_audit_results, get_audit_report
from app.services.keyword_service import mark_report_failed
from app.services.claude_client import stream_claude_response
from app.services.prompt_builder import build_audit_prompt
from app.services.auth_service import require_auth
from app.services.stream_manager import create_stream, get_stream, remove_stream
from app.models.user import User

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_audit(req: AnalyzeRequest, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    report = await create_audit_report(db, req.query, req.project_id)
    report_id = str(report.id)
    create_stream(report_id)
    asyncio.create_task(_run_analysis(report_id, req.query))
    return AnalyzeResponse(report_id=report.id, stream_url=f"/api/audit/stream/{report_id}")


async def _run_analysis(report_id: str, query: str):
    queue = get_stream(report_id)
    full_text = ""
    try:
        async with async_session() as db:
            report = await db.get(Report, uuid.UUID(report_id))
            if report:
                report.status = ReportStatus.STREAMING
                await db.commit()

        prompt = build_audit_prompt(query)
        async for chunk in stream_claude_response(prompt):
            full_text += chunk
            await queue.put({"event": "chunk", "data": chunk})

        async with async_session() as db:
            await save_audit_results(db, uuid.UUID(report_id), full_text)
        await queue.put({"event": "done", "data": report_id})
    except Exception as e:
        async with async_session() as db:
            await mark_report_failed(db, uuid.UUID(report_id), str(e))
        await queue.put({"event": "error", "data": str(e)})
    finally:
        await queue.put(None)


@router.get("/stream/{report_id}")
async def stream_audit(report_id: str):
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


@router.get("/{report_id}", response_model=AuditReportOut)
async def get_audit(report_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    report = await get_audit_report(db, report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    ar = report.audit_results[0] if report.audit_results else None
    return AuditReportOut(
        report=ReportOut.model_validate(report),
        audit_result=AuditResultOut.model_validate(ar) if ar else None,
    )
