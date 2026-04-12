from pydantic import BaseModel, validator
from typing import Optional


class AnalyzeRequest(BaseModel):
    code: str
    language: Optional[str] = "unknown"
    source: Optional[str] = "paste"

    @validator("code")
    def code_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("code must not be empty or whitespace")
        return v

    @validator("source")
    def source_must_be_valid(cls, v):
        if v not in ("paste", "manual", "unknown", "auto"):
            raise ValueError("source must be 'paste', 'manual', 'auto', or 'unknown'")
        return v


class AnalyzeResponse(BaseModel):
    explanation: str
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    model: str = "gemini"
    status: str = "success"


class ErrorResponse(BaseModel):
    error: str
    status: str = "error"