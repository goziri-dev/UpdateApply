from pydantic import Field
from pydantic import BaseModel

class ParseJobPostingRequest(BaseModel):
    description: str = Field(..., min_length=1, description="Raw job posting text")