import asyncio
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, async_session
from app.models.report import Report, ReportModule, ReportStatus
from app.schemas.report import AnalyzeRequest, AnalyzeResponse
from app.services.claude_client import stream_claude_response
from app.services.prompt_builder import PROMPT_BUILDERS
from app.services.keyword_service import save_keyword_results, mark_report_failed
from app.services.competitor_service import save_competitor_results
from app.services.content_service import save_content_results
from app.services.audit_service import save_audit_results
from app.services.auth_service import require_auth
from app.services.stream_manager import create_stream, get_stream, remove_stream
from app.services.webhook_service import notify_report_completed, notify_report_failed
from app.models.user import User

router = APIRouter(prefix="/api/workflows", tags=["workflows"])

WORKFLOW_MODULES = {
    "full": ["keywords", "competitor", "content", "audit"],
    "strategy": ["keywords", "competitor", "content"],
    "fix": ["audit"],
}

WORKFLOW_MODULE_MAP = {
    "full": ReportModule.FULL,
    "strategy": ReportModule.STRATEGY,
    "fix": ReportModule.FIX,
}

SAVE_FUNCTIONS = {
    "keywords": save_keyword_results,
    "competitor": save_competitor_results,
    "content": save_content_results,
    "audit": save_audit_results,
}


@router.post("/{workflow_type}", response_model=AnalyzeResponse)
async def start_workflow(workflow_type: str, req: AnalyzeRequest, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    if workflow_type not in WORKFLOW_MODULES:
        raise HTTPException(400, f"Unknown workflow: {workflow_type}")

    report = Report(
        module=WORKFLOW_MODULE_MAP[workflow_type],
        input_query=req.query,
        status=ReportStatus.PENDING,
        project_id=req.project_id,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    report_id = str(report.id)
    create_stream(report_id)
    asyncio.create_task(_run_workflow(report_id, req.query, workflow_type))

    return AnalyzeResponse(
        report_id=report.id,
        stream_url=f"/api/workflows/{workflow_type}/stream/{report_id}",
    )


async def _run_workflow(report_id: str, query: str, workflow_type: str):
    queue = get_stream(report_id)
    modules = WORKFLOW_MODULES[workflow_type]
    all_markdown = ""

    try:
        async with async_session() as db:
            report = await db.get(Report, uuid.UUID(report_id))
            if report:
                report.status = ReportStatus.STREAMING
                await db.commit()

        for i, module in enumerate(modules):
            header = f"\n\n{'='*60}\n## Module: {module.upper()} ({i+1}/{len(modules)})\n{'='*60}\n\n"
            await queue.put({"event": "chunk", "data": header})
            all_markdown += header

            prompt = PROMPT_BUILDERS[module](query)
            module_text = ""
            async for chunk in stream_claude_response(prompt):
                module_text += chunk
                all_markdown += chunk
                await queue.put({"event": "chunk", "data": chunk})

            # Save module-specific results
            async with async_session() as db:
                await SAVE_FUNCTIONS[module](db, uuid.UUID(report_id), module_text)

        # Update the main report
        async with async_session() as db:
            report = await db.get(Report, uuid.UUID(report_id))
            if report:
                report.raw_markdown = all_markdown
                report.status = ReportStatus.COMPLETED
                report.summary = f"{workflow_type.title()} workflow completed for {query}"
                await db.commit()

        await queue.put({"event": "done", "data": report_id})
        await notify_report_completed(workflow_type, query, report_id)
    except Exception as e:
        async with async_session() as db:
            await mark_report_failed(db, uuid.UUID(report_id), str(e))
        await queue.put({"event": "error", "data": str(e)})
        await notify_report_failed(workflow_type, query, str(e))
    finally:
        await queue.put(None)


@router.get("/{workflow_type}/stream/{report_id}")
async def stream_workflow(workflow_type: str, report_id: str):
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
