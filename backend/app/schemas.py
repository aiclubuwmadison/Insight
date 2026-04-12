from pydantic import BaseModel
from typing import Optional


class AnalyzeRequest(BaseModel):
    code: str
    language: str
    source: Optional[str] = "vscode"


class AnalyzeResponse(BaseModel):
    success: bool
    explanation: Optional[str] = None
    error: Optional[str] = None