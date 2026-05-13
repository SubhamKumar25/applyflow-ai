"""Foundit (formerly Monster India) adapter."""
from __future__ import annotations

import logging
from urllib.parse import quote_plus

from app.models.job import JobListing
from automation.browser import launch_persistent_context
from automation.human_behavior import human_delay
from automation.platforms.base import BasePlatformAdapter

logger = logging.getLogger("applyflow.automation.foundit")


class FounditAdapter(BasePlatformAdapter):
    name = "foundit"

    async def search_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 20,
        remote_only: bool = False,
    ) -> list[JobListing]:
        from playwright.async_api import async_playwright

        url = f"https://www.foundit.in/srp/results?query={quote_plus(keywords)}"
        if location:
            url += f"&locations={quote_plus(location)}"

        results: list[JobListing] = []
        async with async_playwright() as pw:
            ctx = await launch_persistent_context(pw, self.name)
            page = await ctx.new_page()
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await human_delay(2500, 4500)

                cards = await page.query_selector_all(".srpResultCardContainer, .cardContainer, [data-job-id]")
                for card in cards[:limit]:
                    try:
                        title_el = await card.query_selector(".jobTitle, h3.jobTitle")
                        company_el = await card.query_selector(".companyName")
                        loc_el = await card.query_selector(".location, .jobLocation")
                        link_el = await card.query_selector("a")

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
                            url=href if href.startswith("http") else "https://www.foundit.in" + href,
                            platform=self.name,
                            is_remote=("remote" in loc.lower()),
                        ))
                    except Exception as e:
                        logger.warning(f"Failed to parse Foundit card: {e}")
            finally:
                await ctx.close()
        return results

    async def apply_to_job(self, job, resume_path, cover_letter, ai_answer_fn) -> dict:
        return {"status": "skipped", "detail": "Foundit apply uses Human Verification Mode"}
