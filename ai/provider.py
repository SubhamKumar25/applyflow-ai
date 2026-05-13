"""Unified AI provider interface — supports OpenAI and Gemini, swappable via env."""
from __future__ import annotations

import json
import logging
from typing import Any

from app.config import settings

logger = logging.getLogger("applyflow.ai")


class AIProvider:
    """Abstract interface for an LLM provider."""

    async def complete(self, prompt: str, system: str = "", json_mode: bool = False) -> str:
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    def __init__(self) -> None:
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def complete(self, prompt: str, system: str = "", json_mode: bool = False) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        kwargs: dict[str, Any] = {"model": self.model, "messages": messages}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        resp = await self.client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content or ""


class GeminiProvider(AIProvider):
    def __init__(self) -> None:
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.genai = genai
        self.model_name = settings.GEMINI_MODEL

    async def complete(self, prompt: str, system: str = "", json_mode: bool = False) -> str:
        full_prompt = (system + "\n\n" + prompt) if system else prompt
        if json_mode:
            full_prompt += "\n\nRespond with valid JSON only. No markdown fences."

        model = self.genai.GenerativeModel(self.model_name)
        resp = await model.generate_content_async(full_prompt)
        return resp.text or ""


class FallbackProvider(AIProvider):
    """No-op provider used when API keys are missing. Returns deterministic, useful stubs
    so the app still works end-to-end during development."""

    async def complete(self, prompt: str, system: str = "", json_mode: bool = False) -> str:
        logger.warning("Using FallbackProvider — set AI_PROVIDER + API key for real AI output")
        if json_mode:
            return json.dumps({
                "skills": ["python", "javascript", "react", "fastapi", "mongodb"],
                "experience": [],
                "education": [],
                "projects": [],
                "contact": {},
                "ats_score": 65.0,
                "suggestions": [
                    "Add more quantified achievements (e.g., 'Reduced load time by 40%').",
                    "Include relevant keywords for ATS optimization.",
                    "Add a professional summary at the top.",
                ],
                "match_score": 70.0,
                "matching_skills": [],
                "missing_skills": [],
                "relevance_reasons": ["Skills alignment", "Experience level match"],
                "remote_compatible": True,
            })
        return (
            "Dear Hiring Manager,\n\n"
            "I'm writing to express my interest in this role. My background aligns "
            "well with your requirements, and I'm excited about the opportunity to contribute.\n\n"
            "Best regards,\nApplicant\n\n[Configure AI_PROVIDER and an API key to generate real cover letters]"
        )


def get_provider() -> AIProvider:
    if settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        return OpenAIProvider()
    if settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        return GeminiProvider()
    return FallbackProvider()


def safe_json_parse(text: str) -> dict:
    """Robust JSON parse — strips markdown fences and falls back to {}."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1] if "```" in text[3:] else text[3:]
        if text.startswith("json"):
            text = text[4:].strip()
        text = text.rsplit("```", 1)[0].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning(f"Failed to parse JSON from AI: {text[:200]}")
        return {}
