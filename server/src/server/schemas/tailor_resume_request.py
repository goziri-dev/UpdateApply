from pydantic import BaseModel, Field

from server.schemas.candidate import Candidate
from server.schemas.job_posting import JobPosting
from server.schemas.tailored_resume import ResumeStyle


class TailorResumeRequest(BaseModel):
    """Request body for tailoring a candidate CV to a job posting."""

    candidate: Candidate
    job: JobPosting
    style: ResumeStyle = Field(
        ResumeStyle.CLASSIC,
        description="HTML template style: classic or compact",
    )
