"""Base adapter — every platform implements the same interface."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.job import JobListing


class BasePlatformAdapter(ABC):
    name: str = "base"

    @abstractmethod
    async def search_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 20,
        remote_only: bool = False,
    ) -> list[JobListing]:
        """Search for jobs and return a list of JobListing objects."""

    @abstractmethod
    async def apply_to_job(
        self,
        job: JobListing,
        resume_path: str,
        cover_letter: str,
        ai_answer_fn,
    ) -> dict:
        """Apply to a single job. Returns {status: 'applied'|'failed'|'skipped', detail: str}."""

    async def login(self, username: str, password: str) -> bool:
        """Optional — adapters that require auth implement this."""
        return True
