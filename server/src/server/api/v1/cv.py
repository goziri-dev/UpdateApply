from fastapi import APIRouter, File, HTTPException, UploadFile

from server.schemas.candidate import Candidate
from server.services.agent import Task, create_agent
from server.services.pdf import InvalidOrEmptyPDF, convert_pdf_to_markdown

cv_router = APIRouter(prefix="/cv")


@cv_router.post("/process")
async def process_cv(cv: UploadFile = File(...)):
    filename = (cv.filename or "").lower()
    if cv.content_type != "application/pdf" and filename.endswith(".pdf"):
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
        system_prompt=(
            "Extract only basic contact/identity info from the cv markdown.\n"
            "Use null for anything not clearly present. Do not invent details."
        ),
        structured_output=Candidate,
    )

    candidate = await agent.invoke(text)
    return candidate
