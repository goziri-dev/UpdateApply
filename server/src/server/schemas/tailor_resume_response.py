from pydantic import BaseModel, Field

from server.schemas.tailored_resume import ResumeStyle, TailoredResume


class TailorResumeResponse(BaseModel):
    """Tailored resume plus filled HTML for client-side PDF rendering."""

    resume: TailoredResume
    html: str = Field(..., description="Filled HTML document for the chosen style")
    style: ResumeStyle
