from datetime import datetime

from pydantic import BaseModel, Field


class ResumeData(BaseModel):
    user_id: str
    filename: str
    file_path: str
    raw_text: str = ""
    skills: list[str] = Field(default_factory=list)
    experience: list[dict] = Field(default_factory=list)
    education: list[dict] = Field(default_factory=list)
    projects: list[dict] = Field(default_factory=list)
    contact: dict = Field(default_factory=dict)
    ats_score: float = 0.0
    suggestions: list[str] = Field(default_factory=list)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class ResumeResponse(BaseModel):
    id: str
    filename: str
    skills: list[str]
    experience: list[dict]
    education: list[dict]
    projects: list[dict]
    ats_score: float
    suggestions: list[str]
    uploaded_at: datetime


class ATSScoreResponse(BaseModel):
    score: float
    breakdown: dict
    suggestions: list[str]
    keyword_matches: list[str]
    missing_keywords: list[str]
