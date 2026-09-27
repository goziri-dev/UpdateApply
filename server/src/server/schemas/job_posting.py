from pydantic import BaseModel, Field


class JobPosting(BaseModel):
    """Structured fields extracted from a job posting, keywords first."""

    title: str | None = Field(None, description="Job title")
    company: str | None = Field(None, description="Company name")
    location: str | None = Field(None, description="Location or remote")
    employment_type: str | None = Field(
        None, description="Full-time, part-time, contract, etc."
    )
    seniority: str | None = Field(None, description="Junior, mid, senior, etc.")
    qualifications: list[str] = Field(
        default_factory=list,
        description=(
            "Keywords/qualifications from Requirements, Qualifications, Must Have, "
            "Need to Have, What we are Looking for, and similar sections"
        ),
    )
    preferred_qualifications: list[str] = Field(
        default_factory=list,
        description="Nice-to-have / preferred qualifications if clearly separated",
    )
    responsibilities: list[str] = Field(
        default_factory=list,
        description="Day-to-day duties if listed (secondary to qualifications)",
    )
    salary_range: str | None = Field(None, description="Salary if mentioned")
