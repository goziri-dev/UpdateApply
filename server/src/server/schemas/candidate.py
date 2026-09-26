from pydantic import BaseModel, EmailStr, Field


class Candidate(BaseModel):
    """Basic identity/contact info extracted from a jobseeker's CV."""

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
