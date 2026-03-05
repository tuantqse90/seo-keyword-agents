import re
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.report import Report, ReportModule, ReportStatus
from app.models.competitor import Competitor, KeywordGap
from app.services.parser import parse_competitor_response


def _safe_int(val) -> int | None:
    if val is None:
        return None
    if isinstance(val, int):
        return val
    try:
        cleaned = re.sub(r"[^\d]", "", str(val))
        return int(cleaned) if cleaned else None
    except (ValueError, TypeError):
        return None


async def create_competitor_report(db: AsyncSession, query: str, project_id: uuid.UUID | None = None) -> Report:
    report = Report(
        module=ReportModule.COMPETITOR,
        input_query=query,
        status=ReportStatus.PENDING,
        project_id=project_id,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


async def save_competitor_results(db: AsyncSession, report_id: uuid.UUID, raw_markdown: str) -> None:
    report = await db.get(Report, report_id)
    if not report:
        return

    parsed = parse_competitor_response(raw_markdown)
    report.raw_markdown = raw_markdown
    report.summary = parsed.get("summary", "")
    report.status = ReportStatus.COMPLETED

    for comp_data in parsed.get("competitors", []):
        # Ensure top_keywords, strengths, weaknesses are stored as JSONB-compatible dicts/lists
        top_kw = comp_data.get("top_keywords")
        if isinstance(top_kw, list):
            top_kw = {"items": top_kw}
        strengths = comp_data.get("strengths")
        if isinstance(strengths, list):
            strengths = {"items": strengths}
        weaknesses = comp_data.get("weaknesses")
        if isinstance(weaknesses, list):
            weaknesses = {"items": weaknesses}

        comp = Competitor(
            report_id=report_id,
            name=comp_data.get("name", ""),
            url=comp_data.get("url"),
            estimated_traffic=_safe_int(comp_data.get("estimated_traffic")),
            domain_authority=_safe_int(comp_data.get("domain_authority")),
            top_keywords=top_kw,
            strengths=strengths,
            weaknesses=weaknesses,
        )
        db.add(comp)

    for gap_data in parsed.get("keyword_gaps", []):
        gap = KeywordGap(
            report_id=report_id,
            keyword=gap_data.get("keyword", ""),
            target_rank=_safe_int(gap_data.get("target_rank")),
            competitor_ranks=gap_data.get("competitor_ranks"),
        )
        db.add(gap)

    await db.commit()


async def get_competitor_report(db: AsyncSession, report_id: uuid.UUID) -> Report | None:
    stmt = (
        select(Report)
        .where(Report.id == report_id)
        .options(selectinload(Report.competitors), selectinload(Report.keyword_gaps))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
