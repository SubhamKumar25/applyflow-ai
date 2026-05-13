"""Orchestrates job search across multiple platforms."""
from __future__ import annotations

import asyncio
import logging

from app.models.job import JobListing, JobSearchQuery
from automation.platforms import get_adapter

logger = logging.getLogger("applyflow.automation.search")


async def search_all_platforms(query: JobSearchQuery) -> list[JobListing]:
    """Search every requested platform in parallel and merge the results."""
    tasks = []
    for platform in query.platforms:
        try:
            adapter = get_adapter(platform)
        except ValueError:
            logger.warning(f"Skipping unknown platform: {platform}")
            continue
        tasks.append(_safe_search(adapter, query))

    nested = await asyncio.gather(*tasks)
    merged: list[JobListing] = []
    for batch in nested:
        merged.extend(batch)
    return merged[: query.limit * len(query.platforms)]


async def _safe_search(adapter, query: JobSearchQuery) -> list[JobListing]:
    try:
        return await adapter.search_jobs(
            keywords=query.keywords,
            location=query.location,
            limit=query.limit,
            remote_only=query.remote_only,
        )
    except Exception as e:
        logger.exception(f"{adapter.name} search failed: {e}")
        return []
