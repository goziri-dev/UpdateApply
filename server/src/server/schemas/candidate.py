from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field


class ExperienceKind(StrEnum):
    WORK = "work"
    INTERNSHIP = "internship"


class EducationEntry(BaseModel):
    """A degree or formal education line from the CV."""

    degree: str | None = Field(None, description="Degree type, e.g. B.A., M.S., PhD")
    field: str | None = Field(None, description="Field of study")
    institution: str | None = Field(None, description="School or university name")
    graduation: str | None = Field(
        None,
        description=(
            "Graduation year if within the last 3 years; otherwise 'Graduated' "
            "when a past graduation is clear; null if unknown"
        ),
    )


class CertificateEntry(BaseModel):
    """A professional certificate or license from the CV."""

    name: str = Field(..., description="Certificate or license name")
    active: bool | None = Field(
        None, description="True if still active/valid when stated; null if unknown"
    )


class ExperienceBullet(BaseModel):
    """A single bullet as written on the CV — do not invent or embellish."""

    text: str = Field(..., description="Bullet text exactly as on the CV (or close paraphrase)")


class WorkExperience(BaseModel):
    """Paid work or internship role (paid by a company)."""

    kind: ExperienceKind = Field(
        ExperienceKind.WORK,
        description="work for paid employment; internship for internships",
    )
    title: str | None = Field(None, description="Job or internship title")
    company: str | None = Field(None, description="Employer or organization name")
    location: str | None = Field(None, description="City/state or remote if present")
    start_date: str | None = Field(
        None, description="Start date as Month Year when available, e.g. Jan 2020"
    )
    end_date: str | None = Field(
        None,
        description="End date as Month Year, or 'current' if still employed",
    )
    summary: str | None = Field(
        None,
        description="Role overview sentence if present on the CV; otherwise null",
    )
    bullets: list[ExperienceBullet] = Field(
        default_factory=list,
        description="Achievement/responsibility bullets for this role",
    )


class Project(BaseModel):
    """Unpaid personal/academic project (no dates per resume guide)."""

    title: str | None = Field(None, description="Project name")
    summary: str | None = Field(
        None, description="One-line project overview if present; otherwise null"
    )
    bullets: list[ExperienceBullet] = Field(
        default_factory=list,
        description="Up to a few bullets describing the project",
    )


class Candidate(BaseModel):
    """Full structured profile extracted from a jobseeker's CV."""

    full_name: str | None = Field(None, description="Candidate's full name")
    email: EmailStr | None = Field(None, description="Primary email address")
    phone: str | None = Field(None, description="Phone number as written on the CV")
    location: str | None = Field(None, description="City/region/country if present")
    linkedin_url: str | None = Field(
        None, description="LinkedIn profile URL if present"
    )
    website_url: str | None = Field(
        None, description="Personal site or portfolio URL if present"
    )
    work_authorization: str | None = Field(
        None,
        description=(
            "Work authorization if stated, e.g. US Citizen, Green Card Holder; "
            "null if not on the CV"
        ),
    )
    languages: list[str] = Field(
        default_factory=list,
        description="Languages listed on the CV",
    )
    summary: str | None = Field(
        None,
        description=(
            "Only if the CV already notes industry change, relocation, or visa/"
            "sponsorship needs; otherwise null — do not invent a summary"
        ),
    )
    education: list[EducationEntry] = Field(default_factory=list)
    certificates: list[CertificateEntry] = Field(default_factory=list)
    work_history: list[WorkExperience] = Field(
        default_factory=list,
        description="Paid work and internships, newest first, about last 12 years",
    )
    projects: list[Project] = Field(
        default_factory=list,
        description="Unpaid projects (not paid by a company)",
    )
