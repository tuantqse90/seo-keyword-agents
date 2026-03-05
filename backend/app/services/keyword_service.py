import re
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.report import Report, ReportModule, ReportStatus
from app.models.keyword import Keyword
from app.services.parser import parse_keywords_response


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


def _safe_float(val) -> float | None:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    try:
        cleaned = re.sub(r"[^\d.]", "", str(val))
        return float(cleaned) if cleaned else None
    except (ValueError, TypeError):
        return None


async def create_keyword_report(db: AsyncSession, query: str, project_id: uuid.UUID | None = None) -> Report:
    report = Report(
        module=ReportModule.KEYWORDS,
        input_query=query,
        status=ReportStatus.PENDING,
        project_id=project_id,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


async def save_keyword_results(db: AsyncSession, report_id: uuid.UUID, raw_markdown: str) -> None:
    report = await db.get(Report, report_id)
    if not report:
        return

    parsed = parse_keywords_response(raw_markdown)
    report.raw_markdown = raw_markdown
    report.summary = parsed.get("summary", "")
    report.status = ReportStatus.COMPLETED

    for kw_data in parsed.get("keywords", []):
        keyword = Keyword(
            report_id=report_id,
            keyword=kw_data.get("keyword", ""),
            cluster=kw_data.get("cluster"),
            search_volume=_safe_int(kw_data.get("search_volume")),
            keyword_difficulty=_safe_int(kw_data.get("keyword_difficulty")),
            search_intent=kw_data.get("search_intent"),
            cpc=_safe_float(kw_data.get("cpc")),
            opportunity_score=_safe_int(kw_data.get("opportunity_score")),
            is_golden=bool(kw_data.get("is_golden", False)),
        )
        db.add(keyword)

    await db.commit()


async def get_keyword_report(db: AsyncSession, report_id: uuid.UUID) -> Report | None:
    stmt = select(Report).where(Report.id == report_id).options(selectinload(Report.keywords))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def mark_report_failed(db: AsyncSession, report_id: uuid.UUID, error: str) -> None:
    report = await db.get(Report, report_id)
    if report:
        report.status = ReportStatus.FAILED
        report.summary = f"Error: {error}"
        await db.commit()
