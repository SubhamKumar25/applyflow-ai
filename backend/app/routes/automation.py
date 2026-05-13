from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/automation", tags=["Automation"])


@router.get("/status")
async def get_automation_status(user: dict = Depends(get_current_user)):
    user_settings = user.get("settings", {})
    return {
        "auto_mode": user_settings.get("auto_mode", False),
        "daily_limit": user_settings.get("daily_apply_limit", 20),
        "platforms": user_settings.get("platforms", []),
        "scheduler_running": False,
    }


@router.put("/settings")
async def update_automation_settings(
    settings_update: dict,
    user: dict = Depends(get_current_user),
):
    db = get_db()
    allowed_keys = {"daily_apply_limit", "auto_mode", "platforms", "notifications"}
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
async def start_automation(user: dict = Depends(get_current_user)):
    db = get_db()
    resume = await db.resumes.find_one({"user_id": user["id"], "is_active": True})
    if not resume:
        return {"status": "error", "message": "Please upload a resume first"}

    return {
        "status": "started",
        "message": "Automation started. Jobs will be searched and applied based on your settings.",
    }


@router.post("/stop")
async def stop_automation(user: dict = Depends(get_current_user)):
    return {"status": "stopped", "message": "Automation stopped."}
