from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class JobListing(BaseModel):
    title: str
    company: str
    location: str = ""
    description: str = ""
    url: str = ""
    platform: str = ""
    job_type: str = ""
    salary: str = ""
    posted_date: str = ""
    is_remote: bool = False
    easy_apply: bool = False
    scraped_at: datetime = Field(default_factory=datetime.utcnow)


class JobMatch(BaseModel):
    job: JobListing
    match_score: float = 0.0
    missing_skills: list[str] = Field(default_factory=list)
    matching_skills: list[str] = Field(default_factory=list)
    relevance_reasons: list[str] = Field(default_factory=list)
    remote_compatible: bool = False


class ApplicationLog(BaseModel):
    user_id: str
    job_title: str
    company: str
    platform: str
    url: str = ""
    status: Literal["applied", "pending", "failed", "skipped", "interview", "rejected", "offered"] = "pending"
    cover_letter: str = ""
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    notes: str = ""
    ai_answers: dict = Field(default_factory=dict)


class ApplicationResponse(BaseModel):
    id: str
    job_title: str
    company: str
    platform: str
    status: str
    applied_at: datetime
    url: str = ""


class JobSearchQuery(BaseModel):
    keywords: str
    location: str = ""
    platforms: list[str] = Field(default_factory=lambda: ["linkedin", "indeed"])
    remote_only: bool = False
    job_type: str = ""
    experience_level: str = ""
    limit: int = 20


class CoverLetterRequest(BaseModel):
    job_title: str
    company: str
    job_description: str
    tone: str = "professional"


class ApplyJobRequest(BaseModel):
    """Client sends the full listing so the server can apply without a prior job cache."""

    job: JobListing


class ApplyQueuedResponse(BaseModel):
    application_id: str
    status: str = "pending"
    message: str = "Application queued"
