import asyncio
import uuid
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db, async_session
from app.models.report import Report, ReportModule, ReportStatus
from app.models.audit import AuditResult
from app.schemas.report import AnalyzeResponse, ReportOut, ReportListOut
from app.services.export_service import export_csv, export_pdf_html
from app.services.auth_service import require_auth
from app.models.user import User

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/stats")
async def report_stats(db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    """Dashboard statistics: total, by module, by status, and daily counts."""
    # Total
    total = await db.scalar(select(func.count(Report.id)))

    # By module
    module_stmt = select(Report.module, func.count(Report.id)).group_by(Report.module)
    module_result = await db.execute(module_stmt)
    by_module = {row[0].value: row[1] for row in module_result.all()}

    # By status
    status_stmt = select(Report.status, func.count(Report.id)).group_by(Report.status)
    status_result = await db.execute(status_stmt)
    by_status = {row[0].value: row[1] for row in status_result.all()}

    # Daily counts (last 30 days)
    daily_stmt = (
        select(
            cast(Report.created_at, Date).label("date"),
            func.count(Report.id).label("count"),
        )
        .group_by("date")
        .order_by("date")
        .limit(30)
    )
    daily_result = await db.execute(daily_stmt)
    daily = [{"date": str(row.date), "count": row.count} for row in daily_result.all()]

    return {
        "total": total or 0,
        "by_module": by_module,
        "by_status": by_status,
        "daily": daily,
    }


@router.get("/search", response_model=list[ReportListOut])
async def search_reports(
    q: str = Query(..., min_length=1, max_length=255),
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Full-text search across report queries and markdown content."""
    pattern = f"%{q}%"
    stmt = (
        select(Report)
        .where(
            (Report.input_query.ilike(pattern))
            | (Report.raw_markdown.ilike(pattern))
            | (Report.summary.ilike(pattern))
        )
        .order_by(Report.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("", response_model=list[ReportListOut])
async def list_reports(
    module: ReportModule | None = None,
    status: ReportStatus | None = None,
    project_id: uuid.UUID | None = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    stmt = select(Report).order_by(Report.created_at.desc())
    if module:
        stmt = stmt.where(Report.module == module)
    if status:
        stmt = stmt.where(Report.status == status)
    if project_id:
        stmt = stmt.where(Report.project_id == project_id)
    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{report_id}", response_model=ReportOut)
async def get_report(report_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    report = await db.get(Report, report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    return report


@router.delete("/{report_id}", status_code=204)
async def delete_report(report_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    report = await db.get(Report, report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    await db.delete(report)
    await db.commit()


@router.post("/{report_id}/retry", response_model=AnalyzeResponse)
async def retry_report(report_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    """Retry a failed report by creating a new analysis with the same query."""
    report = await db.get(Report, report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    if report.status not in (ReportStatus.FAILED,):
        raise HTTPException(400, "Only failed reports can be retried")

    module = report.module.value
    query = report.input_query
    project_id = report.project_id

    from app.routers import keywords, competitor, content, audit, workflows
    from app.services.stream_manager import create_stream

    module_map = {
        "keywords": (keywords._run_analysis, "/api/keywords/stream"),
        "competitor": (competitor._run_analysis, "/api/competitor/stream"),
        "content": (content._run_analysis, "/api/content/stream"),
        "audit": (audit._run_analysis, "/api/audit/stream"),
    }

    if module in ("full", "strategy", "fix"):
        new_report = Report(
            module=report.module, input_query=query,
            status=ReportStatus.PENDING, project_id=project_id,
        )
        db.add(new_report)
        await db.commit()
        await db.refresh(new_report)
        rid = str(new_report.id)
        create_stream(rid)
        asyncio.create_task(workflows._run_workflow(rid, query, module))
        return AnalyzeResponse(report_id=new_report.id, stream_url=f"/api/workflows/{module}/stream/{rid}")

    if module in module_map:
        from app.services.keyword_service import create_keyword_report
        from app.services.competitor_service import create_competitor_report
        from app.services.content_service import create_content_report
        from app.services.audit_service import create_audit_report

        create_fns = {
            "keywords": create_keyword_report,
            "competitor": create_competitor_report,
            "content": create_content_report,
            "audit": create_audit_report,
        }
        new_report = await create_fns[module](db, query, project_id)
        rid = str(new_report.id)
        run_fn, url_prefix = module_map[module]
        create_stream(rid)
        asyncio.create_task(run_fn(rid, query))
        return AnalyzeResponse(report_id=new_report.id, stream_url=f"{url_prefix}/{rid}")

    raise HTTPException(400, f"Cannot retry module: {module}")


@router.get("/{report_id}/export/csv")
async def export_report_csv(report_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    stmt = (
        select(Report)
        .where(Report.id == report_id)
        .options(
            selectinload(Report.keywords),
            selectinload(Report.competitors),
            selectinload(Report.audit_results).selectinload(AuditResult.issues),
        )
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(404, "Report not found")

    csv_content = await export_csv(db, report)
    return StreamingResponse(
        BytesIO(csv_content.encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=report_{report_id}.csv"},
    )


@router.get("/{report_id}/export/pdf")
async def export_report_pdf(report_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    stmt = (
        select(Report)
        .where(Report.id == report_id)
        .options(
            selectinload(Report.keywords),
            selectinload(Report.competitors),
            selectinload(Report.audit_results).selectinload(AuditResult.issues),
        )
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(404, "Report not found")

    html_content = await export_pdf_html(db, report)

    try:
        from weasyprint import HTML
        pdf_bytes = HTML(string=html_content).write_pdf()
    except ImportError:
        # weasyprint not installed — return HTML
        return StreamingResponse(
            BytesIO(html_content.encode()),
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename=report_{report_id}.html"},
        )

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"},
    )
