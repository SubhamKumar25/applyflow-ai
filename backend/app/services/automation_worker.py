"""Background automation: saved search + optional auto-apply."""
from __future__ import annotations

import os
from datetime import datetime, timezone

from bson import ObjectId

from app.activity_log import write_log
from app.database import get_db
from app.models.job import JobListing, JobSearchQuery
from ai.answer_generator import generate_answer
from ai.cover_letter import generate_cover_letter
from ai.matcher import match_jobs_with_resume
from automation.apply import apply_to_jobs
from automation.job_search import search_all_platforms


async def run_user_automation_cycle(user_id: str) -> None:
    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return
    settings = user.get("settings") or {}
    ss = settings.get("saved_search") or {}
    keywords = (ss.get("keywords") or "").strip()
    if not keywords:
        await write_log(user_id, "Automation: add saved search keywords in Automation settings", "warning")
        return

    resume = await db.resumes.find_one({"user_id": user_id, "is_active": True})
    if not resume:
        await write_log(user_id, "Automation: upload a resume first", "warning")
        return

    query = JobSearchQuery(
        keywords=keywords,
        location=(ss.get("location") or "").strip(),
        platforms=ss.get("platforms") or ["linkedin", "indeed"],
        remote_only=bool(ss.get("remote_only", False)),
        limit=int(ss.get("limit", 12)),
    )

    jobs = await search_all_platforms(query)
    matched = await match_jobs_with_resume(jobs, resume)
    matched.sort(key=lambda m: m.match_score, reverse=True)
    await write_log(
        user_id,
        f"Automation: found {len(matched)} ranked matches",
        "info",
        {"keywords": keywords, "raw_jobs": len(jobs)},
    )

    if not settings.get("auto_mode"):
        await write_log(
            user_id,
            "Semi-auto: open Job Matches to review and use Apply on listings.",
            "info",
            {"match_count": len(matched)},
        )
        return

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    applied_today = await db.applications.count_documents({
        "user_id": user_id,
        "applied_at": {"$gte": today_start},
        "status": "applied",
    })
    daily_limit = int(settings.get("daily_apply_limit", 20))
    remaining = max(0, daily_limit - applied_today)
    if remaining <= 0:
        await write_log(user_id, "Automation: daily apply limit reached", "warning")
        return

    take_n = min(3, remaining, len(matched))
    if take_n == 0:
        return

    to_apply = [m.job for m in matched[:take_n]]
    resume_path = resume.get("file_path") or ""
    if not resume_path or not os.path.isfile(resume_path):
        await write_log(user_id, "Automation: resume file missing on server", "error")
        return

    async def cover_fn(j: JobListing) -> str:
        return await generate_cover_letter(
            resume_data=resume,
            job_title=j.title,
            company=j.company,
            job_description=j.description or "",
            tone="professional",
        )

    async def answer_fn(question: str, j: JobListing) -> str:
        return await generate_answer(question, resume, j.title, j.company)

    async def on_progress(result: dict) -> None:
        await db.applications.insert_one({
            "user_id": user_id,
            "job_title": result.get("job_title", ""),
            "company": result.get("company", ""),
            "platform": result.get("platform", ""),
            "url": result.get("url", ""),
            "status": "applied",
            "applied_at": datetime.now(timezone.utc),
            "notes": (result.get("detail") or "")[:500],
            "cover_letter": "",
            "ai_answers": {},
        })

    results = await apply_to_jobs(
        user_id,
        to_apply,
        resume_path,
        cover_fn,
        answer_fn,
        daily_limit=remaining,
        on_progress=on_progress,
        inter_job_delay=True,
    )

    for r in results:
        if r.get("status") == "applied":
            continue
        await db.applications.insert_one({
            "user_id": user_id,
            "job_title": r.get("job_title", ""),
            "company": r.get("company", ""),
            "platform": r.get("platform", ""),
            "url": r.get("url", ""),
            "status": r.get("status", "failed"),
            "applied_at": datetime.now(timezone.utc),
            "notes": (r.get("detail") or "")[:500],
            "cover_letter": "",
            "ai_answers": {},
        })

    await write_log(
        user_id,
        f"Automation batch finished ({len(results)} job(s))",
        "info",
        {"results": [r.get("status") for r in results]},
    )
