"""AI job matcher — scores jobs against a resume."""
from app.models.job import JobListing, JobMatch
from ai.provider import get_provider, safe_json_parse

MATCH_PROMPT_TEMPLATE = """You are an expert job-matching engine.

Given a candidate's resume profile and a job listing, score the match.

CANDIDATE SKILLS: {skills}
CANDIDATE EXPERIENCE SUMMARY: {experience}

JOB TITLE: {job_title}
COMPANY: {company}
LOCATION: {location}
JOB DESCRIPTION: {description}

Return a JSON object:
{{
  "match_score": <float 0-100>,
  "matching_skills": [skills from candidate that match the job],
  "missing_skills": [skills required by the job that candidate lacks],
  "relevance_reasons": [2-3 short reasons why this job is/is not a good fit],
  "remote_compatible": <true|false>
}}
"""


async def match_single_job(job: JobListing, resume: dict) -> JobMatch:
    provider = get_provider()
    skills = resume.get("skills", [])
    experience = resume.get("experience", [])
    experience_summary = "; ".join(
        f"{e.get('role', '')} at {e.get('company', '')}" for e in experience[:5]
    )

    prompt = MATCH_PROMPT_TEMPLATE.format(
        skills=", ".join(skills[:30]) or "N/A",
        experience=experience_summary or "N/A",
        job_title=job.title,
        company=job.company,
        location=job.location,
        description=(job.description or "")[:3000],
    )
    response = await provider.complete(
        prompt=prompt,
        system="You are a JSON-only job matching API.",
        json_mode=True,
    )
    data = safe_json_parse(response)

    return JobMatch(
        job=job,
        match_score=float(data.get("match_score", 0.0)),
        matching_skills=data.get("matching_skills", []),
        missing_skills=data.get("missing_skills", []),
        relevance_reasons=data.get("relevance_reasons", []),
        remote_compatible=bool(data.get("remote_compatible", False)),
    )


async def match_jobs_with_resume(jobs: list[JobListing], resume: dict) -> list[JobMatch]:
    import asyncio

    # Cap concurrency to avoid rate-limiting
    sem = asyncio.Semaphore(4)

    async def _bounded(job: JobListing) -> JobMatch:
        async with sem:
            try:
                return await match_single_job(job, resume)
            except Exception:
                # Fallback to a simple keyword overlap score so we never crash the whole batch
                skills = set(s.lower() for s in resume.get("skills", []))
                desc = (job.description or "").lower() + " " + job.title.lower()
                matching = [s for s in skills if s in desc]
                score = min(100.0, len(matching) * 8.0)
                return JobMatch(
                    job=job,
                    match_score=score,
                    matching_skills=matching,
                    missing_skills=[],
                    relevance_reasons=["Keyword overlap (AI unavailable)"],
                    remote_compatible="remote" in (job.location or "").lower(),
                )

    return await asyncio.gather(*[_bounded(j) for j in jobs])
