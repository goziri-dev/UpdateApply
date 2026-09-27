from pydantic import BaseModel, Field


class ParseJobPostingRequest(BaseModel):
    description: str = Field(..., min_length=1, description="Raw job posting text")