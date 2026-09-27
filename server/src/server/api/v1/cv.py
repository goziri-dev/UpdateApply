from fastapi import APIRouter, File, HTTPException, UploadFile

from server.schemas.candidate import Candidate
from server.services.agent import Task, create_agent
from server.services.pdf import InvalidOrEmptyPDF, convert_pdf_to_markdown
from server.services.resume_normalize import normalize_education_entry

cv_router = APIRouter(prefix="/cv")

_PROCESS_CV_PROMPT = """\
Extract a full structured candidate profile from the CV markdown.

Rules:
- Capture contact info, work authorization, and languages when present.
- Include education and certificates as separate lists.
- Education degree field: abbreviations only (B.A., B.S., M.A., M.S., PhD, MBA) — never "Bachelor of Science" etc.
- Put paid roles and internships in work_history (kind=work or internship).
- Put unpaid personal/academic work in projects (no dates).
- Preserve bullet text as written; do not invent employers, degrees, metrics, or dates.
- Prefer Month Year for start/end dates; use "current" for end_date when still employed.
- Prefer newest roles first; focus on roughly the last 12 years of experience.
- summary: only if the CV already notes industry change, relocation, or visa/sponsorship needs; otherwise null.
- Use null or empty lists for anything not clearly present.
"""


@cv_router.post("/process")
async def process_cv(cv: UploadFile = File(...)):
    filename = (cv.filename or "").lower()
    if cv.content_type != "application/pdf" and not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="CV must be PDF")

    data = await cv.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty pdf file")

    try:
        text = await convert_pdf_to_markdown(data)
    except InvalidOrEmptyPDF as e:
        raise HTTPException(status_code=400, detail=e.detail)

    agent = create_agent(
        Task.PROCESS_CV,
        system_prompt=_PROCESS_CV_PROMPT,
        structured_output=Candidate,
    )

    candidate = await agent.invoke(text)
    if candidate.education:
        candidate = candidate.model_copy(
            update={
                "education": [
                    normalize_education_entry(e) for e in candidate.education
                ],
            }
        )
    return candidate
