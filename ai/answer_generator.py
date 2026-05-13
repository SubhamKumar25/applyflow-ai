"""AI answer generator for job application form questions."""
from ai.provider import get_provider


async def generate_answer(
    question: str,
    resume_data: dict,
    job_title: str = "",
    company: str = "",
    max_chars: int = 500,
) -> str:
    provider = get_provider()
    contact = resume_data.get("contact", {}) or {}
    skills = ", ".join(resume_data.get("skills", [])[:15])
    experience = "; ".join(
        f"{e.get('role', '')} at {e.get('company', '')} ({e.get('duration', '')})"
        for e in (resume_data.get("experience") or [])[:4]
    )

    prompt = f"""You're filling a job application form. Answer the question below in the candidate's voice.

CANDIDATE:
- Name: {contact.get('name', 'Applicant')}
- Skills: {skills}
- Experience: {experience}

JOB: {job_title} at {company}

QUESTION: {question}

Rules:
- Be concise (max {max_chars} characters)
- Answer truthfully based on the candidate's profile
- For yes/no questions, answer "Yes" or "No" + 1 short sentence of justification
- For numeric questions (years of experience, salary), give a reasonable number
- For "Why this role/company" questions, be specific
- No placeholders, no markdown
"""

    answer = await provider.complete(
        prompt=prompt,
        system="You answer job application questions concisely and truthfully.",
    )
    return answer.strip()[:max_chars]
