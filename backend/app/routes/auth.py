from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.config import settings
from app.database import get_db
from app.models.user import (
    GoogleAuthRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def new_user_settings() -> dict:
    return {
        "daily_apply_limit": 20,
        "auto_mode": False,
        "automation_active": False,
        "platforms": ["linkedin", "indeed", "naukri", "internshala", "wellfound", "foundit"],
        "notifications": {"telegram": False, "email": False},
        "theme": "dark",
        "saved_search": {
            "keywords": "",
            "location": "",
            "platforms": ["linkedin", "indeed"],
            "remote_only": False,
            "limit": 12,
        },
    }


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate):
    db = get_db()
    email_norm = str(data.email).lower()
    existing = await db.users.find_one({"email": email_norm})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_doc = {
        "name": data.name,
        "email": email_norm,
        "hashed_password": hash_password(data.password),
        "created_at": datetime.now(timezone.utc),
        "settings": new_user_settings(),
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    token = create_access_token(user_id)

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user_id,
            name=data.name,
            email=email_norm,
            created_at=user_doc["created_at"],
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    db = get_db()
    email = str(data.email).lower()
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    hp = user.get("hashed_password")
    if not hp:
        raise HTTPException(status_code=401, detail="Use Google to sign in")

    if not verify_password(data.password, hp):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = str(user["_id"])
    token = create_access_token(user_id)

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user_id,
            name=user["name"],
            email=user["email"],
            created_at=user["created_at"],
        ),
    )


@router.post("/google", response_model=TokenResponse)
async def google_auth(body: GoogleAuthRequest):
    if not settings.GOOGLE_CLIENT_ID.strip():
        raise HTTPException(
            status_code=503,
            detail="Google sign-in is not configured (set GOOGLE_CLIENT_ID on the server)",
        )

    try:
        from google.auth.transport import requests as ga_requests
        from google.oauth2 import id_token

        idinfo = id_token.verify_oauth2_token(
            body.credential,
            ga_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired Google token")

    if not idinfo.get("email_verified"):
        raise HTTPException(status_code=400, detail="Google email is not verified")

    email = (idinfo.get("email") or "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Google account has no email")

    name = (idinfo.get("name") or email.split("@")[0]).strip()[:100]
    sub = str(idinfo.get("sub", ""))

    db = get_db()
    now = datetime.now(timezone.utc)
    user = await db.users.find_one({"email": email})

    if user:
        user_id = str(user["_id"])
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"google_sub": sub, "auth_google": True}},
        )
        user = await db.users.find_one({"_id": user["_id"]})
    else:
        user_doc = {
            "name": name,
            "email": email,
            "hashed_password": None,
            "google_sub": sub,
            "auth_google": True,
            "created_at": now,
            "settings": new_user_settings(),
        }
        result = await db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)
        user = await db.users.find_one({"_id": result.inserted_id})

    if user is None:
        raise HTTPException(status_code=500, detail="Failed to load user after Google sign-in")
    token = create_access_token(user_id)

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user_id,
            name=user["name"],
            email=user["email"],
            created_at=user["created_at"],
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return UserResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        created_at=user["created_at"],
    )
