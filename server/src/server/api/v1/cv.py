from fastapi import APIRouter, File, HTTPException, UploadFile

from server.schemas.candidate import Candidate
from server.services.agent import Task, create_agent
from server.services.pdf import convert_pdf_to_markdown

cv_router = APIRouter(prefix="/cv")

@cv_router.post("/process")
async def process_cv(cv: UploadFile = File(...)):
    if cv.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="CV must be PDF")
    
    md = await convert_pdf_to_markdown(await cv.read())
    text = md if isinstance(md, str) else str(md)
    agent = create_agent(
        Task.PROCESS_CV,
        system_prompt = (
            "Extract only basic contact/identity info from the cv markdown.\n"
            "Use null for anything not clearly present. Do not invent details."
        ),
        structured_output=Candidate
    )
    
    job_profile = await agent.invoke(text)
    return job_profile 