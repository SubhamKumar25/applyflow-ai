"""Internshala adapter (India — internships + entry-level)."""
from __future__ import annotations

import logging

from app.models.job import JobListing
from automation.browser import launch_persistent_context
from automation.human_behavior import human_delay
from automation.platforms.base import BasePlatformAdapter

logger = logging.getLogger("applyflow.automation.internshala")


class InternshalaAdapter(BasePlatformAdapter):
    name = "internshala"

    async def search_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 20,
        remote_only: bool = False,
    ) -> list[JobListing]:
        from playwright.async_api import async_playwright

        slug = keywords.replace(" ", "-").lower()
        url = (
            f"https://internshala.com/internships/work-from-home-{slug}-internships/"
            if remote_only
            else f"https://internshala.com/internships/{slug}-internships/"
        )

        results: list[JobListing] = []
        async with async_playwright() as pw:
            ctx = await launch_persistent_context(pw, self.name)
            page = await ctx.new_page()
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await human_delay(2000, 4000)

                cards = await page.query_selector_all(".individual_internship, .container-fluid.individual_internship")
                for card in cards[:limit]:
                    try:
                        title_el = await card.query_selector(".heading_4_5, h3.heading_4_5")
                        company_el = await card.query_selector(".company_name, .heading_6")
                        link_el = await card.query_selector("a.view_detail_button, .internship_link")

                        title = (await title_el.inner_text()).strip() if title_el else ""
                        company = (await company_el.inner_text()).strip() if company_el else ""
                        href = await link_el.get_attribute("href") if link_el else ""
                        if not title or not href:
                            continue

                        results.append(JobListing(
                            title=title,
                            company=company,
                            location="Remote" if remote_only else "India",
                            url=href if href.startswith("http") else "https://internshala.com" + href,
                            platform=self.name,
                            is_remote=remote_only,
                        ))
                    except Exception as e:
                        logger.warning(f"Failed to parse Internshala card: {e}")
            finally:
                await ctx.close()
        return results

    async def apply_to_job(self, job, resume_path, cover_letter, ai_answer_fn) -> dict:
        return {"status": "skipped", "detail": "Internshala apply uses Human Verification Mode"}
