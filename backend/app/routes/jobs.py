from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.activity_log import write_log
from app.auth import get_current_user
from app.database import get_db
from app.models.job import (
    ApplicationResponse,
    ApplyJobRequest,
    ApplyQueuedResponse,
    CoverLetterRequest,
    JobMatch,
    JobSearchQuery,
)
from app.services.apply_execution import run_pending_application

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/search", response_model=list[JobMatch])
async def search_jobs(query: JobSearchQuery, user: dict = Depends(get_current_user)):
    db = get_db()
    resume = await db.resumes.find_one({"user_id": user["id"], "is_active": True})
    if not resume:
        raise HTTPException(status_code=400, detail="Please upload a resume first")

    from automation.job_search import search_all_platforms

    jobs = await search_all_platforms(query)

    from ai.matcher import match_jobs_with_resume

    matched = await match_jobs_with_resume(jobs, resume)
    await write_log(
        user["id"],
        f"Job search completed ({len(jobs)} listings, {len(matched)} ranked)",
        "info",
        {"keywords": query.keywords, "location": query.location},
    )
    return matched


@router.post("/apply", response_model=ApplyQueuedResponse, status_code=202)
async def apply_job(
    req: ApplyJobRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    db = get_db()
    resume = await db.resumes.find_one({"user_id": user["id"], "is_active": True})
    if not resume:
        raise HTTPException(status_code=400, detail="Please upload a resume first")

    job = req.job
    if not (job.platform or "").strip():
        raise HTTPException(status_code=400, detail="Job platform is required")
    try:
        from automation.platforms import get_adapter

        get_adapter(job.platform)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = await db.applications.count_documents({
        "user_id": user["id"],
        "applied_at": {"$gte": today_start},
        "status": "applied",
    })

    limit = user.get("settings", {}).get("daily_apply_limit", 20)
    if today_count >= limit:
        raise HTTPException(status_code=429, detail=f"Daily apply limit ({limit}) reached")

    now = datetime.now(timezone.utc)
    doc = {
        "user_id": user["id"],
        "job_title": job.title,
        "company": job.company,
        "platform": job.platform,
        "url": job.url or "",
        "status": "pending",
        "applied_at": now,
        "notes": "Queued for browser automation",
        "cover_letter": "",
        "ai_answers": {},
    }
    ins = await db.applications.insert_one(doc)
    app_id = str(ins.inserted_id)

    job_payload = job.model_dump(mode="json")
    background_tasks.add_task(run_pending_application, app_id, user["id"], job_payload)

    await write_log(user["id"], f"Queued apply: {job.title} @ {job.company}", "info", {"application_id": app_id})

    return ApplyQueuedResponse(
        application_id=app_id,
        status="pending",
        message="Application queued — processing in the background.",
    )


@router.post("/cover-letter")
async def generate_cover_letter(req: CoverLetterRequest, user: dict = Depends(get_current_user)):
    db = get_db()
    resume = await db.resumes.find_one({"user_id": user["id"], "is_active": True})
    if not resume:
        raise HTTPException(status_code=400, detail="Please upload a resume first")

    from ai.cover_letter import generate_cover_letter

    letter = await generate_cover_letter(
        resume_data=resume,
        job_title=req.job_title,
        company=req.company,
        job_description=req.job_description,
        tone=req.tone,
    )
    return {"cover_letter": letter}


@router.get("/applications", response_model=list[ApplicationResponse])
async def get_applications(
    status: str | None = None,
    limit: int = 50,
    user: dict = Depends(get_current_user),
):
    db = get_db()
    query_filter: dict = {"user_id": user["id"]}
    if status:
        query_filter["status"] = status

    cursor = db.applications.find(query_filter).sort("applied_at", -1).limit(limit)
    results = []
    async for app in cursor:
        results.append(
            ApplicationResponse(
                id=str(app["_id"]),
                job_title=app["job_title"],
                company=app["company"],
                platform=app["platform"],
                status=app["status"],
                applied_at=app["applied_at"],
                url=app.get("url", ""),
            )
        )
    return results


@router.get("/analytics")
async def get_analytics(user: dict = Depends(get_current_user)):
    db = get_db()
    pipeline = [
        {"$match": {"user_id": user["id"]}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
    ]
    status_counts = {}
    async for doc in db.applications.aggregate(pipeline):
        status_counts[doc["_id"]] = doc["count"]

    platform_pipeline = [
        {"$match": {"user_id": user["id"]}},
        {"$group": {"_id": "$platform", "count": {"$sum": 1}}},
    ]
    platform_counts = {}
    async for doc in db.applications.aggregate(platform_pipeline):
        platform_counts[doc["_id"]] = doc["count"]

    total = sum(status_counts.values())

    return {
        "total_applications": total,
        "by_status": status_counts,
        "by_platform": platform_counts,
        "applied": status_counts.get("applied", 0),
        "pending": status_counts.get("pending", 0),
        "skipped": status_counts.get("skipped", 0),
        "interview": status_counts.get("interview", 0),
        "rejected": status_counts.get("rejected", 0),
        "offered": status_counts.get("offered", 0),
    }
