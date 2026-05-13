"""Apply orchestrator — applies to a list of jobs, respecting daily limit + human pauses."""
from __future__ import annotations

import asyncio
import logging
import random
from datetime import datetime, timezone
from typing import Awaitable, Callable

from app.config import settings
from app.models.job import JobListing
from automation.platforms import get_adapter

logger = logging.getLogger("applyflow.automation.apply")


async def apply_to_jobs(
    user_id: str,
    jobs: list[JobListing],
    resume_path: str,
    cover_letter_fn: Callable[[JobListing], Awaitable[str]],
    ai_answer_fn: Callable[[str], Awaitable[str]],
    daily_limit: int | None = None,
    on_progress: Callable[[dict], Awaitable[None]] | None = None,
) -> list[dict]:
    limit = daily_limit or settings.DAILY_APPLY_LIMIT
    results: list[dict] = []
    applied = 0

    for job in jobs:
        if applied >= limit:
            logger.info(f"Daily apply limit ({limit}) reached")
            break
        try:
            adapter = get_adapter(job.platform)
            cover_letter = await cover_letter_fn(job)
            result = await adapter.apply_to_job(job, resume_path, cover_letter, ai_answer_fn)
            result["job_title"] = job.title
            result["company"] = job.company
            result["platform"] = job.platform
            result["url"] = job.url
            result["timestamp"] = datetime.now(timezone.utc).isoformat()
            results.append(result)

            if result.get("status") == "applied":
                applied += 1
                if on_progress:
                    await on_progress(result)

            # Human-like break between applications
            await asyncio.sleep(random.uniform(30, 90))
        except Exception as e:
            logger.exception(f"Failed to apply to {job.title} @ {job.company}: {e}")
            results.append({
                "status": "failed",
                "detail": str(e),
                "job_title": job.title,
                "company": job.company,
                "platform": job.platform,
            })
    return results
