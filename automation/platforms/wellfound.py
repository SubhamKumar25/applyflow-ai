"""Wellfound (formerly AngelList Talent) adapter — startup jobs."""
from __future__ import annotations

import logging
from urllib.parse import quote_plus

from app.models.job import JobListing
from automation.browser import launch_persistent_context
from automation.human_behavior import human_delay
from automation.platforms.base import BasePlatformAdapter

logger = logging.getLogger("applyflow.automation.wellfound")


class WellfoundAdapter(BasePlatformAdapter):
    name = "wellfound"

    async def search_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 20,
        remote_only: bool = False,
    ) -> list[JobListing]:
        from playwright.async_api import async_playwright

        url = f"https://wellfound.com/jobs?role={quote_plus(keywords)}"
        if remote_only:
            url += "&remote=true"

        results: list[JobListing] = []
        async with async_playwright() as pw:
            ctx = await launch_persistent_context(pw, self.name)
            page = await ctx.new_page()
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await human_delay(2500, 4500)

                cards = await page.query_selector_all("[data-test='JobSearchCard'], .styles_component__uTjje")
                for card in cards[:limit]:
                    try:
                        title_el = await card.query_selector("h2, a[href*='/jobs/']")
                        company_el = await card.query_selector("[data-test='startup-link']")

                        title = (await title_el.inner_text()).strip() if title_el else ""
                        company = (await company_el.inner_text()).strip() if company_el else ""
                        href = await title_el.get_attribute("href") if title_el else ""
                        if not title or not href:
                            continue

                        results.append(JobListing(
                            title=title,
                            company=company,
                            location=location or "Various",
                            url=href if href.startswith("http") else "https://wellfound.com" + href,
                            platform=self.name,
                            is_remote=remote_only,
                        ))
                    except Exception as e:
                        logger.warning(f"Failed to parse Wellfound card: {e}")
            finally:
                await ctx.close()
        return results

    async def apply_to_job(self, job, resume_path, cover_letter, ai_answer_fn) -> dict:
        return {"status": "skipped", "detail": "Wellfound apply uses Human Verification Mode"}
