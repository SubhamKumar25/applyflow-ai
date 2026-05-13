"""Persist user-facing activity logs to MongoDB (collection: logs)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.database import get_db


async def write_log(
    user_id: str,
    message: str,
    level: str = "info",
    meta: dict[str, Any] | None = None,
) -> None:
    db = get_db()
    await db.logs.insert_one({
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc),
        "level": level,
        "message": message,
        "meta": meta or {},
    })
