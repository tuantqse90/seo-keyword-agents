import re
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.report import Report, ReportModule, ReportStatus
from app.models.audit import AuditResult, AuditIssue
from app.services.parser import parse_audit_response


async def create_audit_report(db: AsyncSession, query: str, project_id: uuid.UUID | None = None) -> Report:
    report = Report(
        module=ReportModule.AUDIT,
        input_query=query,
        status=ReportStatus.PENDING,
        project_id=project_id,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


async def save_audit_results(db: AsyncSession, report_id: uuid.UUID, raw_markdown: str) -> None:
    report = await db.get(Report, report_id)
    if not report:
        return

    parsed = parse_audit_response(raw_markdown)
    report.raw_markdown = raw_markdown
    report.summary = parsed.get("summary", "")
    report.status = ReportStatus.COMPLETED

    def _safe_int(val):
        if val is None: return None
        if isinstance(val, int): return val
        try:
            cleaned = re.sub(r"[^\d]", "", str(val))
            return int(cleaned) if cleaned else None
        except (ValueError, TypeError): return None

    # Ensure quick_wins/tech_checklist are JSONB-compatible
    quick_wins = parsed.get("quick_wins")
    if isinstance(quick_wins, list):
        quick_wins = {"items": quick_wins}
    tech_checklist = parsed.get("tech_checklist")

    audit_result = AuditResult(
        report_id=report_id,
        overall_score=_safe_int(parsed.get("overall_score")),
        letter_grade=str(parsed.get("letter_grade", ""))[:5] or None,
        quick_wins=quick_wins,
        tech_checklist=tech_checklist,
    )
    db.add(audit_result)
    await db.flush()

    for issue_data in parsed.get("issues", []):
        issue = AuditIssue(
            audit_result_id=audit_result.id,
            severity=issue_data.get("severity", "Info"),
            category=issue_data.get("category", ""),
            title=issue_data.get("title", ""),
            description=issue_data.get("description"),
            fix_suggestion=issue_data.get("fix_suggestion"),
            code_snippet=issue_data.get("code_snippet"),
            effort_level=issue_data.get("effort_level"),
        )
        db.add(issue)

    await db.commit()


async def get_audit_report(db: AsyncSession, report_id: uuid.UUID) -> Report | None:
    stmt = (
        select(Report)
        .where(Report.id == report_id)
        .options(selectinload(Report.audit_results).selectinload(AuditResult.issues))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
