"""Run a single job application (Playwright + AI) and update MongoDB."""
from __future__ import annotations

import os
from datetime import datetime, timezone

from bson import ObjectId

from app.activity_log import write_log
from app.database import get_db
from app.models.job import JobListing
from app.notifications import notify_user
from ai.answer_generator import generate_answer
from ai.cover_letter import generate_cover_letter
from automation.apply import apply_to_jobs


async def run_pending_application(application_id: str, user_id: str, job_dict: dict) -> None:
    """Background task: execute apply pipeline and set applications.status."""
    db = get_db()
    try:
        oid = ObjectId(application_id)
    except Exception:
        return
    try:
        job = JobListing.model_validate(job_dict)
    except Exception as e:
        await db.applications.update_one(
            {"_id": oid},
            {"$set": {"status": "failed", "notes": f"Invalid job payload: {e}", "applied_at": datetime.now(timezone.utc)}},
        )
        return

    resume = await db.resumes.find_one({"user_id": user_id, "is_active": True})
    if not resume:
        await db.applications.update_one(
            {"_id": oid},
            {"$set": {"status": "failed", "notes": "No active resume", "applied_at": datetime.now(timezone.utc)}},
        )
        return

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    settings = (user or {}).get("settings") or {}
    daily_limit = int(settings.get("daily_apply_limit", 20))

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    applied_today = await db.applications.count_documents({
        "user_id": user_id,
        "applied_at": {"$gte": today_start},
        "status": "applied",
    })
    if applied_today >= daily_limit:
        await db.applications.update_one(
            {"_id": oid},
            {"$set": {
                "status": "skipped",
                "notes": "Daily apply limit reached",
                "applied_at": datetime.now(timezone.utc),
            }},
        )
        await write_log(user_id, f"Apply skipped (limit): {job.title} @ {job.company}", "warning", {"application_id": application_id})
        return

    resume_path = resume.get("file_path") or ""
    if not resume_path or not os.path.isfile(resume_path):
        await db.applications.update_one(
            {"_id": oid},
            {"$set": {"status": "failed", "notes": "Resume file missing on server", "applied_at": datetime.now(timezone.utc)}},
        )
        await write_log(user_id, f"Apply failed (missing file): {job.title}", "error", {"application_id": application_id})
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

    try:
        results = await apply_to_jobs(
            user_id,
            [job],
            resume_path,
            cover_fn,
            answer_fn,
            daily_limit=1,
            on_progress=None,
            inter_job_delay=False,
        )
    except Exception as e:
        await db.applications.update_one(
            {"_id": oid},
            {"$set": {"status": "failed", "notes": str(e), "applied_at": datetime.now(timezone.utc)}},
        )
        await write_log(user_id, f"Apply exception: {job.title} — {e}", "error", {"application_id": application_id})
        return

    result = results[0] if results else {"status": "failed", "detail": "empty result"}
    raw_status = result.get("status", "failed")
    if raw_status == "applied":
        final = "applied"
    elif raw_status == "skipped":
        final = "skipped"
    else:
        final = "failed"

    notes = result.get("detail", "") or ""
    await db.applications.update_one(
        {"_id": oid},
        {"$set": {
            "status": final,
            "notes": notes[:2000],
            "applied_at": datetime.now(timezone.utc),
            "url": job.url or "",
            "job_title": job.title,
            "company": job.company,
            "platform": job.platform,
        }},
    )

    await write_log(
        user_id,
        f"Apply {final}: {job.title} @ {job.company} ({job.platform})",
        "info" if final == "applied" else "warning",
        {"application_id": application_id, "detail": notes[:500]},
    )

    notif = settings.get("notifications") or {}
    if final == "applied" and (notif.get("telegram") or notif.get("email")):
        msg = f"ApplyFlow: Applied to *{job.title}* at {job.company} ({job.platform})."
        await notify_user(msg, email=user.get("email") if notif.get("email") else None)
