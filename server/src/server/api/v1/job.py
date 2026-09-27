from server.schemas.parse_job_posting_request import ParseJobPostingRequest
from server.schemas.job_posting import JobPosting
from server.services.agent import create_agent, Task
from fastapi import APIRouter

job_router = APIRouter(prefix="/job")

@job_router.post("/parse")
async def parse_job(job: ParseJobPostingRequest):
    system_prompt = (
        "Extract structured fields from this job posting.\n"
        "Use null/empty lists for anything not clearly presented. Do not invent details."
    )
    agent = create_agent(
        Task.PARSE_JOB_POSTING, 
        system_prompt=system_prompt, 
        structured_output=JobPosting
    )
    job_posting = await agent.invoke(job.description)
    return job_posting