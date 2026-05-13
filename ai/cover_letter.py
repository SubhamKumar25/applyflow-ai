"""AI cover letter generator."""
from ai.provider import get_provider

COVER_LETTER_PROMPT = """Write a personalized, professional cover letter for the following.

Candidate profile:
- Name: {name}
- Top skills: {skills}
- Experience summary: {experience}

Job:
- Title: {job_title}
- Company: {company}
- Description: {job_description}

Tone: {tone}

Requirements:
- 3-4 short paragraphs (~250 words)
- Open with genuine interest in {company} and the {job_title} role
- Tie 2-3 candidate skills/experiences directly to the JD
- Mention one specific thing about the company (if discernible from JD)
- Close with a call to action
- NO clichés ("dynamic team player", "hit the ground running")
- NO placeholders like [Your Name] or [Company]
"""


async def generate_cover_letter(
    resume_data: dict,
    job_title: str,
    company: str,
    job_description: str,
    tone: str = "professional",
) -> str:
    provider = get_provider()
    contact = resume_data.get("contact", {}) or {}
    name = contact.get("name", "Applicant")
    skills = ", ".join(resume_data.get("skills", [])[:10])
    experience = "; ".join(
        f"{e.get('role', '')} at {e.get('company', '')}"
        for e in (resume_data.get("experience") or [])[:3]
    )

    prompt = COVER_LETTER_PROMPT.format(
        name=name,
        skills=skills or "various technical skills",
        experience=experience or "professional experience",
        job_title=job_title,
        company=company,
        job_description=job_description[:3000],
        tone=tone,
    )

    return await provider.complete(
        prompt=prompt,
        system="You write concise, sincere, high-quality cover letters.",
    )
