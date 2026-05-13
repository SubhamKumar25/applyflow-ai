from fastapi import APIRouter, BackgroundTasks, Depends

from app.auth import get_current_user
from app.config import settings as app_settings
from app.database import get_db

router = APIRouter(prefix="/automation", tags=["Automation"])


@router.get("/status")
async def get_automation_status(user: dict = Depends(get_current_user)):
    user_settings = user.get("settings", {})
    return {
        "auto_mode": user_settings.get("auto_mode", False),
        "automation_active": user_settings.get("automation_active", False),
        "daily_limit": user_settings.get("daily_apply_limit", 20),
        "platforms": user_settings.get("platforms", []),
        "notifications": user_settings.get("notifications", {"telegram": False, "email": False}),
        "saved_search": user_settings.get("saved_search", {}),
        "scheduler_enabled": app_settings.SCHEDULER_ENABLED,
    }


@router.put("/settings")
async def update_automation_settings(
    settings_update: dict,
    user: dict = Depends(get_current_user),
):
    db = get_db()
    allowed_keys = {
        "daily_apply_limit",
        "auto_mode",
        "platforms",
        "notifications",
        "saved_search",
        "automation_active",
    }
    update_data = {}
    for key in allowed_keys:
        if key in settings_update:
            update_data[f"settings.{key}"] = settings_update[key]

    if update_data:
        from bson import ObjectId

        await db.users.update_one(
            {"_id": ObjectId(user["id"])},
            {"$set": update_data},
        )

    return {"status": "updated", "updated_fields": list(update_data.keys())}


@router.post("/start")
async def start_automation(
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    db = get_db()
    resume = await db.resumes.find_one({"user_id": user["id"], "is_active": True})
    if not resume:
        return {"status": "error", "message": "Please upload a resume first"}

    from bson import ObjectId

    await db.users.update_one(
        {"_id": ObjectId(user["id"])},
        {"$set": {"settings.automation_active": True}},
    )

    from app.services.automation_worker import run_user_automation_cycle

    background_tasks.add_task(run_user_automation_cycle, user["id"])

    return {
        "status": "started",
        "message": "Automation started — running saved search (and auto-apply if full auto is enabled).",
    }


@router.post("/stop")
async def stop_automation(user: dict = Depends(get_current_user)):
    db = get_db()
    from bson import ObjectId

    await db.users.update_one(
        {"_id": ObjectId(user["id"])},
        {"$set": {"settings.automation_active": False}},
    )
    return {"status": "stopped", "message": "Automation stopped."}
