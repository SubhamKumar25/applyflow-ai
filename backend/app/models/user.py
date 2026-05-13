from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    """ID token (JWT) from Google Identity Services / @react-oauth/google `credential`."""

    credential: str = Field(..., min_length=10)


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime


class UserInDB(BaseModel):
    name: str
    email: str
    hashed_password: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    settings: dict = Field(default_factory=lambda: {
        "daily_apply_limit": 20,
        "auto_mode": False,
        "platforms": ["linkedin", "indeed", "naukri", "internshala", "wellfound", "foundit"],
        "notifications": {"telegram": False, "email": False},
        "theme": "dark",
    })


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
