"""Analytics router — user activity, popular modules, usage trends."""

import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, cast, Date, case, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.report import Report, ReportModule, ReportStatus
from app.models.user import User
from app.services.auth_service import require_auth, require_admin

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
async def analytics_overview(
    days: int = Query(30, le=365),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """High-level analytics: totals, success rate, avg per day."""
    since = datetime.utcnow() - timedelta(days=days)

    # Total reports in period
    total = await db.scalar(
        select(func.count(Report.id)).where(Report.created_at >= since)
    ) or 0

    # By status
    status_stmt = (
        select(Report.status, func.count(Report.id))
        .where(Report.created_at >= since)
        .group_by(Report.status)
    )
    status_result = await db.execute(status_stmt)
    by_status = {row[0].value: row[1] for row in status_result.all()}

    completed = by_status.get("completed", 0)
    failed = by_status.get("failed", 0)
    success_rate = round(completed / (completed + failed) * 100, 1) if (completed + failed) > 0 else 0
    avg_per_day = round(total / max(days, 1), 1)

    return {
        "period_days": days,
        "total_reports": total,
        "by_status": by_status,
        "success_rate": success_rate,
        "avg_per_day": avg_per_day,
    }


@router.get("/popular-modules")
async def popular_modules(
    days: int = Query(30, le=365),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Most used modules ranked by usage count."""
    since = datetime.utcnow() - timedelta(days=days)

    stmt = (
        select(Report.module, func.count(Report.id).label("count"))
        .where(Report.created_at >= since)
        .group_by(Report.module)
        .order_by(func.count(Report.id).desc())
    )
    result = await db.execute(stmt)
    modules = [{"module": row[0].value, "count": row[1]} for row in result.all()]

    return {"period_days": days, "modules": modules}


@router.get("/daily-trend")
async def daily_trend(
    days: int = Query(30, le=365),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Daily report counts for charting."""
    since = datetime.utcnow() - timedelta(days=days)

    stmt = (
        select(
            cast(Report.created_at, Date).label("date"),
            func.count(Report.id).label("total"),
            func.count(case((Report.status == ReportStatus.COMPLETED, 1))).label("completed"),
            func.count(case((Report.status == ReportStatus.FAILED, 1))).label("failed"),
        )
        .where(Report.created_at >= since)
        .group_by("date")
        .order_by("date")
    )
    result = await db.execute(stmt)
    daily = [
        {"date": str(row.date), "total": row.total, "completed": row.completed, "failed": row.failed}
        for row in result.all()
    ]

    return {"period_days": days, "daily": daily}


@router.get("/hourly-heatmap")
async def hourly_heatmap(
    days: int = Query(30, le=365),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Report counts by hour of day and day of week for heatmap visualization."""
    since = datetime.utcnow() - timedelta(days=days)

    stmt = (
        select(
            extract("dow", Report.created_at).label("dow"),
            extract("hour", Report.created_at).label("hour"),
            func.count(Report.id).label("count"),
        )
        .where(Report.created_at >= since)
        .group_by("dow", "hour")
        .order_by("dow", "hour")
    )
    result = await db.execute(stmt)
    heatmap = [
        {"day_of_week": int(row.dow), "hour": int(row.hour), "count": row.count}
        for row in result.all()
    ]

    return {"period_days": days, "heatmap": heatmap}


@router.get("/top-queries")
async def top_queries(
    days: int = Query(30, le=365),
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Most analyzed queries/URLs."""
    since = datetime.utcnow() - timedelta(days=days)

    stmt = (
        select(Report.input_query, func.count(Report.id).label("count"))
        .where(Report.created_at >= since)
        .group_by(Report.input_query)
        .order_by(func.count(Report.id).desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    queries = [{"query": row[0], "count": row[1]} for row in result.all()]

    return {"period_days": days, "queries": queries}


@router.get("/module-success-rates")
async def module_success_rates(
    days: int = Query(30, le=365),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Success/failure rates per module."""
    since = datetime.utcnow() - timedelta(days=days)

    stmt = (
        select(
            Report.module,
            func.count(Report.id).label("total"),
            func.count(case((Report.status == ReportStatus.COMPLETED, 1))).label("completed"),
            func.count(case((Report.status == ReportStatus.FAILED, 1))).label("failed"),
        )
        .where(Report.created_at >= since)
        .group_by(Report.module)
        .order_by(func.count(Report.id).desc())
    )
    result = await db.execute(stmt)
    rates = []
    for row in result.all():
        done = row.completed + row.failed
        rates.append({
            "module": row[0].value,
            "total": row.total,
            "completed": row.completed,
            "failed": row.failed,
            "success_rate": round(row.completed / done * 100, 1) if done > 0 else 0,
        })

    return {"period_days": days, "modules": rates}
