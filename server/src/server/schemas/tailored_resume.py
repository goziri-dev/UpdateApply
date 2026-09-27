from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field

from server.schemas.candidate import (
    CertificateEntry,
    EducationEntry,
    ExperienceKind,
)


class ResumeStyle(StrEnum):
    CLASSIC = "classic"
    COMPACT = "compact"


class TailoredBullet(BaseModel):
    """A resume bullet rewritten for the target job."""

    text: str = Field(
        ...,
        description=(
            "Past-tense What/How/Result bullet, roughly one sentence / one period, "
            "packing relevant job qualifications"
        ),
    )


class TailoredWorkExperience(BaseModel):
    """A work or internship entry on the tailored resume."""

    kind: ExperienceKind = Field(
        ExperienceKind.WORK,
        description="work or internship",
    )
    title: str | None = Field(
        None,
        description=(
            "Common market job title in Title Case (never ALL CAPS). "
            "Prefer alignment with the target job title when duties match; "
            "no (Volunteer) tags or internal mashup titles"
        ),
    )
    company: str | None = Field(None, description="Company name")
    location: str | None = Field(None, description="City/state or remote")
    start_date: str | None = Field(None, description="Month Year start")
    end_date: str | None = Field(
        None, description="Month Year end, or 'current'"
    )
    summary: str = Field(
        ...,
        description=(
            "Past-tense role summary bullet with a few keywords; max ~3 lines, "
            "one period"
        ),
    )
    bullets: list[TailoredBullet] = Field(
        ...,
        min_length=2,
        max_length=7,
        description="2–7 What/How/Result bullets (plus summary = 3–8 total)",
    )


class TailoredProject(BaseModel):
    """A project entry on the tailored resume (no dates)."""

    title: str | None = Field(None, description="Project name")
    summary: str = Field(
        ...,
        description="Past-tense project summary with keywords; one period",
    )
    bullets: list[TailoredBullet] = Field(
        default_factory=list,
        max_length=2,
        description="Up to 2 additional bullets (3 total including summary)",
    )


class TailoredResume(BaseModel):
    """Guide-shaped resume tailored to a specific job posting."""

    full_name: str | None = Field(None, description="Candidate full name")
    email: EmailStr | None = Field(None, description="Email")
    phone: str | None = Field(None, description="Phone")
    location: str | None = Field(None, description="City/state; may include work auth")
    linkedin_url: str | None = Field(None, description="LinkedIn URL")
    website_url: str | None = Field(None, description="Portfolio/site URL")
    languages: list[str] = Field(default_factory=list)
    summary: str | None = Field(
        None,
        description=(
            "Only for industry change, relocation, or visa/sponsorship; "
            "otherwise null — do not invent"
        ),
    )
    education: list[EducationEntry] = Field(default_factory=list)
    certificates: list[CertificateEntry] = Field(default_factory=list)
    work_history: list[TailoredWorkExperience] = Field(
        default_factory=list,
        description="Relevant work/internships, relevance then recency, ≤12 years",
    )
    projects: list[TailoredProject] = Field(default_factory=list)
    keywords_used: list[str] = Field(
        default_factory=list,
        description="Job qualifications woven into the resume bullets",
    )
