import re
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.report import Report, ReportModule, ReportStatus
from app.models.content_brief import ContentBrief
from app.services.parser import parse_content_response


async def create_content_report(db: AsyncSession, query: str, project_id: uuid.UUID | None = None) -> Report:
    report = Report(
        module=ReportModule.CONTENT,
        input_query=query,
        status=ReportStatus.PENDING,
        project_id=project_id,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


async def save_content_results(db: AsyncSession, report_id: uuid.UUID, raw_markdown: str) -> None:
    report = await db.get(Report, report_id)
    if not report:
        return

    parsed = parse_content_response(raw_markdown)
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

    # Ensure JSONB fields are dict/list compatible
    outline = parsed.get("outline")
    if isinstance(outline, list):
        outline = {"sections": outline}
    lsi_keywords = parsed.get("lsi_keywords")
    if isinstance(lsi_keywords, list):
        lsi_keywords = {"items": lsi_keywords}
    eeat_signals = parsed.get("eeat_signals")
    if isinstance(eeat_signals, list):
        eeat_signals = {"items": eeat_signals}

    brief = ContentBrief(
        report_id=report_id,
        title_tag=str(parsed.get("title_tag", ""))[:255] or None,
        meta_description=str(parsed.get("meta_description", ""))[:500] or None,
        target_word_count=_safe_int(parsed.get("target_word_count")),
        outline=outline,
        lsi_keywords=lsi_keywords,
        snippet_strategy=parsed.get("snippet_strategy"),
        eeat_signals=eeat_signals,
    )
    db.add(brief)
    await db.commit()


async def get_content_report(db: AsyncSession, report_id: uuid.UUID) -> Report | None:
    stmt = select(Report).where(Report.id == report_id).options(selectinload(Report.content_briefs))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
