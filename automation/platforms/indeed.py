"""Indeed adapter."""
from __future__ import annotations

import logging
from urllib.parse import urlencode

from app.models.job import JobListing
from automation.browser import launch_persistent_context
from automation.human_behavior import human_delay, human_scroll
from automation.platforms.base import BasePlatformAdapter

logger = logging.getLogger("applyflow.automation.indeed")

BASE_URL = "https://www.indeed.com"


class IndeedAdapter(BasePlatformAdapter):
    name = "indeed"

    async def search_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 20,
        remote_only: bool = False,
    ) -> list[JobListing]:
        from playwright.async_api import async_playwright

        params: dict[str, str] = {"q": keywords}
        if location:
            params["l"] = location
        if remote_only:
            params["sc"] = "0kf:attr(DSQF7);"
        url = f"{BASE_URL}/jobs?{urlencode(params)}"

        results: list[JobListing] = []
        async with async_playwright() as pw:
            ctx = await launch_persistent_context(pw, self.name)
            page = await ctx.new_page()
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await human_delay(2000, 4000)

                for _ in range(2):
                    await human_scroll(page, "down", steps=3)

                cards = await page.query_selector_all("div.job_seen_beacon, .resultContent")
                for card in cards[:limit]:
                    try:
                        title_el = await card.query_selector("h2 a span, .jobTitle span")
                        company_el = await card.query_selector("[data-testid='company-name'], .companyName")
                        loc_el = await card.query_selector("[data-testid='text-location'], .companyLocation")
                        link_el = await card.query_selector("h2 a")

                        title = (await title_el.inner_text()).strip() if title_el else ""
                        company = (await company_el.inner_text()).strip() if company_el else ""
                        loc = (await loc_el.inner_text()).strip() if loc_el else ""
                        href = await link_el.get_attribute("href") if link_el else ""
                        if not title or not href:
                            continue

                        results.append(JobListing(
                            title=title,
                            company=company,
                            location=loc,
                            url=href if href.startswith("http") else BASE_URL + href,
                            platform=self.name,
                            is_remote=("remote" in loc.lower()) or remote_only,
                        ))
                    except Exception as e:
                        logger.warning(f"Failed to parse Indeed card: {e}")
            finally:
                await ctx.close()
        return results

    async def apply_to_job(
        self,
        job: JobListing,
        resume_path: str,
        cover_letter: str,
        ai_answer_fn,
    ) -> dict:
        # Indeed's "Apply now" often redirects to company sites — we mark these as skipped
        # and let the user handle them via Human Verification Mode.
        return {
            "status": "skipped",
            "detail": "Indeed apply requires Human Verification Mode (often redirects off-platform)",
        }
