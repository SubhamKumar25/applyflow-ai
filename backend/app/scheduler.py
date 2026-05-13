"""APScheduler-based daily job search + apply scheduler."""
from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings

logger = logging.getLogger("applyflow.scheduler")

scheduler: AsyncIOScheduler | None = None


async def daily_job_run() -> None:
    """Daily scheduled task — placeholder hook. Real implementation would:
    1. Load each user with auto_mode=true
    2. Pull their preferences (keywords, location, platforms)
    3. Run search_all_platforms() + match_jobs_with_resume()
    4. Apply to top N matches via automation.apply.apply_to_jobs()
    5. Send notification summary
    """
    logger.info("Daily auto-apply run started")
    # TODO: implement once user preferences flow is finalized
    logger.info("Daily auto-apply run finished")


def start_scheduler() -> None:
    global scheduler
    if not settings.SCHEDULER_ENABLED:
        logger.info("Scheduler disabled (SCHEDULER_ENABLED=false)")
        return
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        daily_job_run,
        CronTrigger(
            hour=settings.SCHEDULER_CRON_HOUR,
            minute=settings.SCHEDULER_CRON_MINUTE,
        ),
        id="daily_auto_apply",
    )
    scheduler.start()
    logger.info(
        f"Scheduler started — daily run at {settings.SCHEDULER_CRON_HOUR:02d}:{settings.SCHEDULER_CRON_MINUTE:02d}"
    )


def stop_scheduler() -> None:
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)
        scheduler = None
        logger.info("Scheduler stopped")
