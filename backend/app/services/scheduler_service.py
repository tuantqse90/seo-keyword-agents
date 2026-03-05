"""Simple asyncio-based scheduler that checks for due schedules every 60 seconds."""

import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy import select

from app.database import async_session
from app.models.schedule import Schedule
from app.models.report import ReportModule

logger = logging.getLogger(__name__)

_scheduler_task: asyncio.Task | None = None


async def _run_scheduled_analysis(schedule: Schedule):
    """Trigger an analysis for a due schedule."""
    module = schedule.module.value
    query = schedule.query
    project_id = schedule.project_id

    try:
        if module in ("full", "strategy", "fix"):
            from app.routers import workflows
            from app.models.report import Report, ReportStatus
            async with async_session() as db:
                new_report = Report(
                    module=schedule.module, input_query=query,
                    status=ReportStatus.PENDING, project_id=project_id,
                )
                db.add(new_report)
                await db.commit()
                await db.refresh(new_report)
                rid = str(new_report.id)
                workflows._streams[rid] = asyncio.Queue()
                asyncio.create_task(workflows._run_workflow(rid, query, module))
                logger.info(f"Scheduled workflow {module} started: {rid}")
        else:
            from app.routers import keywords, competitor, content, audit
            from app.services.keyword_service import create_keyword_report
            from app.services.competitor_service import create_competitor_report
            from app.services.content_service import create_content_report
            from app.services.audit_service import create_audit_report

            module_map = {
                "keywords": (create_keyword_report, keywords._run_analysis, keywords._streams),
                "competitor": (create_competitor_report, competitor._run_analysis, competitor._streams),
                "content": (create_content_report, content._run_analysis, content._streams),
                "audit": (create_audit_report, audit._run_analysis, audit._streams),
            }

            if module in module_map:
                create_fn, run_fn, streams = module_map[module]
                async with async_session() as db:
                    new_report = await create_fn(db, query, project_id)
                    rid = str(new_report.id)
                    streams[rid] = asyncio.Queue()
                    asyncio.create_task(run_fn(rid, query))
                    logger.info(f"Scheduled analysis {module} started: {rid}")
    except Exception as e:
        logger.error(f"Scheduled analysis failed for schedule {schedule.id}: {e}")


async def _check_schedules():
    """Check for due schedules and trigger them."""
    while True:
        try:
            now = datetime.utcnow()
            async with async_session() as db:
                stmt = (
                    select(Schedule)
                    .where(Schedule.is_active == True)
                    .where(Schedule.next_run_at <= now)
                )
                result = await db.execute(stmt)
                due_schedules = result.scalars().all()

                for schedule in due_schedules:
                    logger.info(f"Running scheduled analysis: {schedule.module.value} - {schedule.query}")
                    await _run_scheduled_analysis(schedule)

                    schedule.last_run_at = now
                    schedule.next_run_at = now + timedelta(hours=schedule.interval_hours)
                    await db.commit()
        except Exception as e:
            logger.error(f"Scheduler error: {e}")

        await asyncio.sleep(60)


def start_scheduler():
    """Start the background scheduler task."""
    global _scheduler_task
    if _scheduler_task is None or _scheduler_task.done():
        _scheduler_task = asyncio.create_task(_check_schedules())
        logger.info("Scheduler started")


def stop_scheduler():
    """Stop the background scheduler task."""
    global _scheduler_task
    if _scheduler_task and not _scheduler_task.done():
        _scheduler_task.cancel()
        logger.info("Scheduler stopped")
