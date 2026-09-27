from fastapi import APIRouter

from server.schemas.job_posting import JobPosting
from server.schemas.parse_job_posting_request import ParseJobPostingRequest
from server.services.agent import Task, create_agent

job_router = APIRouter(prefix="/job")

_PARSE_JOB_PROMPT = """\
Extract structured fields from this job posting.

Focus on qualifications/keywords from sections like Requirements, Qualifications,
Must Have, Need to Have, What we are Looking for, We Would Love To Meet You If,
and You Might Be a Great Fit If. Put those in qualifications (and preferred_qualifications
when clearly optional/nice-to-have).

Also capture title, company, location, employment_type, seniority, responsibilities,
and salary_range when present. Use null/empty lists for anything not clearly presented.
Do not invent details.
"""


@job_router.post("/parse")
async def parse_job(job: ParseJobPostingRequest):
    agent = create_agent(
        Task.PARSE_JOB_POSTING,
        system_prompt=_PARSE_JOB_PROMPT,
        structured_output=JobPosting,
    )
    job_posting = await agent.invoke(job.description)
    return job_posting
