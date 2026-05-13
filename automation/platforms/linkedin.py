"""LinkedIn adapter — Easy Apply automation.

NOTE: LinkedIn's terms of service restrict automated scraping. Use this responsibly
on your own account with appropriate rate limits. For production use, prefer
LinkedIn's official APIs (Jobs API, Talent Hub) where available.
"""
from __future__ import annotations

import logging
from urllib.parse import urlencode

from app.models.job import JobListing
from automation.browser import launch_persistent_context
from automation.human_behavior import human_click, human_delay, human_scroll
from automation.platforms.base import BasePlatformAdapter

logger = logging.getLogger("applyflow.automation.linkedin")

BASE_URL = "https://www.linkedin.com"


class LinkedInAdapter(BasePlatformAdapter):
    name = "linkedin"

    async def search_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 20,
        remote_only: bool = False,
    ) -> list[JobListing]:
        from playwright.async_api import async_playwright

        params: dict[str, str] = {"keywords": keywords}
        if location:
            params["location"] = location
        if remote_only:
            params["f_WT"] = "2"  # remote filter
        url = f"{BASE_URL}/jobs/search/?{urlencode(params)}"

        results: list[JobListing] = []
        async with async_playwright() as pw:
            ctx = await launch_persistent_context(pw, self.name)
            page = await ctx.new_page()
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await human_delay(2000, 4000)

                # Scroll to load more job cards
                for _ in range(3):
                    await human_scroll(page, "down", steps=3)

                cards = await page.query_selector_all(
                    ".job-search-card, .base-card, [data-job-id]"
                )
                for card in cards[:limit]:
                    try:
                        title_el = await card.query_selector(".base-search-card__title, h3")
                        company_el = await card.query_selector(".base-search-card__subtitle, h4")
                        location_el = await card.query_selector(".job-search-card__location")
                        link_el = await card.query_selector("a[href*='/jobs/view/']")

                        title = (await title_el.inner_text()).strip() if title_el else ""
                        company = (await company_el.inner_text()).strip() if company_el else ""
                        loc = (await location_el.inner_text()).strip() if location_el else ""
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
                            easy_apply=True,
                        ))
                    except Exception as e:
                        logger.warning(f"Failed to parse LinkedIn card: {e}")
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
        from playwright.async_api import async_playwright

        async with async_playwright() as pw:
            ctx = await launch_persistent_context(pw, self.name)
            page = await ctx.new_page()
            try:
                await page.goto(job.url, wait_until="domcontentloaded", timeout=30000)
                await human_delay(1500, 3500)

                # Easy Apply button
                btn = await page.query_selector("button.jobs-apply-button, button[aria-label*='Easy Apply']")
                if not btn:
                    return {"status": "skipped", "detail": "No Easy Apply button"}
                await human_click(page, "button.jobs-apply-button, button[aria-label*='Easy Apply']")
                await human_delay(1500, 3000)

                # Multi-step form loop — find "Next" / "Review" / "Submit application" buttons
                for _ in range(10):
                    submit = await page.query_selector("button[aria-label*='Submit application']")
                    if submit:
                        await human_click(page, "button[aria-label*='Submit application']")
                        await human_delay(2000, 3500)
                        return {"status": "applied", "detail": "Easy Apply submitted"}

                    # Fill any text inputs / textareas that are empty using AI
                    inputs = await page.query_selector_all(
                        "input[type='text']:not([disabled]), textarea:not([disabled])"
                    )
                    for inp in inputs:
                        try:
                            current = (await inp.input_value()) or ""
                            if current.strip():
                                continue
                            label_text = ""
                            label = await inp.evaluate(
                                "el => { const l = el.closest('label') || document.querySelector(`label[for='${el.id}']`); return l ? l.innerText : ''; }"
                            )
                            label_text = (label or "").strip() or "additional info"
                            answer = await ai_answer_fn(label_text)
                            await inp.fill(answer)
                            await human_delay(400, 1000)
                        except Exception as e:
                            logger.debug(f"Could not fill input: {e}")

                    nxt = await page.query_selector("button[aria-label='Continue to next step'], button[aria-label='Review your application']")
                    if nxt:
                        await nxt.click()
                        await human_delay(1500, 3000)
                    else:
                        break

                return {"status": "failed", "detail": "Could not complete multi-step form"}
            except Exception as e:
                logger.exception(f"LinkedIn apply error: {e}")
                return {"status": "failed", "detail": str(e)}
            finally:
                await ctx.close()
