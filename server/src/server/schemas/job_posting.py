from pydantic import Field
from pydantic import BaseModel

class JobPosting(BaseModel):
    """Structured fields extracted from a job posting."""
    title: str | None = Field(None, description="Job title")
    company: str | None = Field(None, description="Company name")
    location: str | None = Field(None, description="Location or remote")
    employment_type: str | None = Field(None, description="Full-time, part-time, contract, etc.")
    seniority: str | None = Field(None, description="Junior, mid, senior, etc.")
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    salary_range: str | None = Field(None, description="Salary if mentioned")