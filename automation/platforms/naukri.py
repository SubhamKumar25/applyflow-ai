"""Naukri.com adapter (India)."""
from __future__ import annotations

import logging

from app.models.job import JobListing
from automation.browser import launch_persistent_context
from automation.human_behavior import human_delay, human_scroll
from automation.platforms.base import BasePlatformAdapter

logger = logging.getLogger("applyflow.automation.naukri")


class NaukriAdapter(BasePlatformAdapter):
    name = "naukri"

    async def search_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 20,
        remote_only: bool = False,
    ) -> list[JobListing]:
        from playwright.async_api import async_playwright

        keyword_slug = keywords.replace(" ", "-").lower()
        location_slug = (location or "").replace(" ", "-").lower()
        url = (
            f"https://www.naukri.com/{keyword_slug}-jobs-in-{location_slug}"
            if location_slug
            else f"https://www.naukri.com/{keyword_slug}-jobs"
        )

        results: list[JobListing] = []
        async with async_playwright() as pw:
            ctx = await launch_persistent_context(pw, self.name)
            page = await ctx.new_page()
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await human_delay(2000, 4000)
                await human_scroll(page, "down", steps=4)

                cards = await page.query_selector_all(".jobTuple, article.jobTuple, .srp-jobtuple-wrapper")
                for card in cards[:limit]:
                    try:
                        title_el = await card.query_selector("a.title, a.jobTuple-title, .title")
                        company_el = await card.query_selector(".companyName, .subTitle, .comp-name")
                        loc_el = await card.query_selector(".location, .locWdth")

                        title = (await title_el.inner_text()).strip() if title_el else ""
                        company = (await company_el.inner_text()).strip() if company_el else ""
                        loc = (await loc_el.inner_text()).strip() if loc_el else ""
                        href = await title_el.get_attribute("href") if title_el else ""
                        if not title or not href:
                            continue

                        results.append(JobListing(
                            title=title,
                            company=company,
                            location=loc,
                            url=href if href.startswith("http") else "https://www.naukri.com" + href,
                            platform=self.name,
                            is_remote=("remote" in loc.lower()),
                        ))
                    except Exception as e:
                        logger.warning(f"Failed to parse Naukri card: {e}")
            finally:
                await ctx.close()
        return results

    async def apply_to_job(self, job, resume_path, cover_letter, ai_answer_fn) -> dict:
        return {"status": "skipped", "detail": "Naukri auto-apply requires logged-in profile + Human Verification Mode"}
