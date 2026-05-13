import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models.resume import ResumeResponse

router = APIRouter(prefix="/resume", tags=["Resume"])


def _extract_text_from_pdf(file_path: str) -> str:
    from PyPDF2 import PdfReader

    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def _extract_text_from_docx(file_path: str) -> str:
    from docx import Document

    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ("pdf", "docx"):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    content = await file.read()
    if len(content) > settings.MAX_RESUME_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large (max {settings.MAX_RESUME_SIZE_MB}MB)")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, f"{user['id']}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(content)

    if ext == "pdf":
        raw_text = _extract_text_from_pdf(file_path)
    else:
        raw_text = _extract_text_from_docx(file_path)

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from resume")

    # AI analysis
    from ai.analyzer import analyze_resume

    analysis = await analyze_resume(raw_text)

    resume_doc = {
        "user_id": user["id"],
        "filename": file.filename,
        "file_path": file_path,
        "raw_text": raw_text,
        "skills": analysis.get("skills", []),
        "experience": analysis.get("experience", []),
        "education": analysis.get("education", []),
        "projects": analysis.get("projects", []),
        "contact": analysis.get("contact", {}),
        "ats_score": analysis.get("ats_score", 0.0),
        "suggestions": analysis.get("suggestions", []),
        "uploaded_at": datetime.now(timezone.utc),
        "is_active": True,
    }

    db = get_db()
    # Deactivate old resumes
    await db.resumes.update_many(
        {"user_id": user["id"], "is_active": True},
        {"$set": {"is_active": False}},
    )

    result = await db.resumes.insert_one(resume_doc)

    return ResumeResponse(
        id=str(result.inserted_id),
        filename=file.filename,
        skills=resume_doc["skills"],
        experience=resume_doc["experience"],
        education=resume_doc["education"],
        projects=resume_doc["projects"],
        ats_score=resume_doc["ats_score"],
        suggestions=resume_doc["suggestions"],
        uploaded_at=resume_doc["uploaded_at"],
    )


@router.get("/active", response_model=ResumeResponse | None)
async def get_active_resume(user: dict = Depends(get_current_user)):
    db = get_db()
    resume = await db.resumes.find_one({"user_id": user["id"], "is_active": True})
    if not resume:
        return None
    return ResumeResponse(
        id=str(resume["_id"]),
        filename=resume["filename"],
        skills=resume.get("skills", []),
        experience=resume.get("experience", []),
        education=resume.get("education", []),
        projects=resume.get("projects", []),
        ats_score=resume.get("ats_score", 0.0),
        suggestions=resume.get("suggestions", []),
        uploaded_at=resume["uploaded_at"],
    )


@router.get("/history")
async def get_resume_history(user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db.resumes.find({"user_id": user["id"]}).sort("uploaded_at", -1).limit(10)
    results = []
    async for resume in cursor:
        results.append(
            ResumeResponse(
                id=str(resume["_id"]),
                filename=resume["filename"],
                skills=resume.get("skills", []),
                experience=resume.get("experience", []),
                education=resume.get("education", []),
                projects=resume.get("projects", []),
                ats_score=resume.get("ats_score", 0.0),
                suggestions=resume.get("suggestions", []),
                uploaded_at=resume["uploaded_at"],
            )
        )
    return results
