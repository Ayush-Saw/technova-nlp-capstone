from pydantic import BaseModel, Field
from typing import Literal

class QARequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    user_role: Literal["public", "staff", "admin"] = "public"

class Citation(BaseModel):
    document_id: str
    title: str
    chunk_id: str

class QAResponse(BaseModel):
    answer: str
    citations: list[Citation]
    refused: bool
    model_version: str

class TriageRequest(BaseModel):
    ticket: str = Field(min_length=5, max_length=8000)

class TriageResponse(BaseModel):
    category: Literal["Authentication", "Billing", "Bug", "Feature Request", "Performance", "Other"]
    priority: Literal["Low", "Medium", "High", "Critical"]
    product_area: str
    summary: str
    model_version: str
