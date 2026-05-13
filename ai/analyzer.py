"""AI resume analyzer — extracts skills, experience, education, projects, ATS score."""
from ai.provider import get_provider, safe_json_parse

RESUME_ANALYSIS_PROMPT = """You are an expert resume analyzer and ATS (Applicant Tracking System) auditor.

Analyze the following resume text and extract structured information.

Return a JSON object with these keys:
{
  "skills": [list of technical/soft skills as lowercase strings],
  "experience": [{"company": "", "role": "", "duration": "", "description": ""}],
  "education": [{"institution": "", "degree": "", "year": ""}],
  "projects": [{"name": "", "description": "", "tech": []}],
  "contact": {"name": "", "email": "", "phone": "", "linkedin": "", "location": ""},
  "ats_score": <float 0-100>,
  "suggestions": [list of 3-5 actionable improvements as strings]
}

ATS scoring criteria (be strict):
- Clear contact info (+10)
- Quantified achievements with numbers/% (+25)
- Technical skills section (+15)
- Action verbs (Led, Built, Designed) (+15)
- Education section (+10)
- Project section (+10)
- Proper structure & length (+15)

RESUME TEXT:
"""


async def analyze_resume(raw_text: str) -> dict:
    provider = get_provider()
    response = await provider.complete(
        prompt=RESUME_ANALYSIS_PROMPT + raw_text[:8000],
        system="You are a precise JSON-only resume analysis API.",
        json_mode=True,
    )
    data = safe_json_parse(response)

    # Defensive defaults
    return {
        "skills": [s.lower() for s in data.get("skills", []) if isinstance(s, str)],
        "experience": data.get("experience", []),
        "education": data.get("education", []),
        "projects": data.get("projects", []),
        "contact": data.get("contact", {}),
        "ats_score": float(data.get("ats_score", 0.0)),
        "suggestions": data.get("suggestions", []),
    }
