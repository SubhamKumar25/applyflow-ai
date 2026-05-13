from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("/")
async def get_logs(limit: int = 100, user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db.logs.find({"user_id": user["id"]}).sort("timestamp", -1).limit(limit)
    results = []
    async for log in cursor:
        log["id"] = str(log["_id"])
        log.pop("_id", None)
        results.append(log)
    return results
