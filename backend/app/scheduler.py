"""APScheduler-based daily job search + apply scheduler."""
from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings

logger = logging.getLogger("applyflow.scheduler")

scheduler: AsyncIOScheduler | None = None


async def daily_job_run() -> None:
    """Daily scheduled task for users with automation_active and saved search keywords."""
    from app.database import get_db
    from app.services.automation_worker import run_user_automation_cycle

    logger.info("Daily auto-apply run started")
    try:
        db = get_db()
        cursor = db.users.find({"settings.automation_active": True})
        async for doc in cursor:
            ss = (doc.get("settings") or {}).get("saved_search") or {}
            if not (ss.get("keywords") or "").strip():
                continue
            uid = str(doc["_id"])
            try:
                await run_user_automation_cycle(uid)
            except Exception as e:
                logger.exception("Daily run failed for user %s: %s", uid, e)
    except Exception as e:
        logger.exception("Daily scheduler run failed: %s", e)
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
