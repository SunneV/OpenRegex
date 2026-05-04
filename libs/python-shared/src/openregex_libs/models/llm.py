from pydantic import BaseModel, Field
from typing import List, Optional


class LLMOptimizeRequest(BaseModel):
    task_id: str = ""
    engine_id: str
    regex: str
    text: str
    flags: List[str] = Field(default_factory=list)


class LLMOptimizeResponse(BaseModel):
    task_id: str
    success: bool
    optimized_regex: str = ""
    flags: List[str] = Field(default_factory=list)
    explanation: str = ""
    error: Optional[str] = None


class LLMGenerateRequest(BaseModel):
    task_id: str = ""
    engine_id: str
    description: str
    text: str
    flags: List[str] = Field(default_factory=list)


class LLMGenerateResponse(BaseModel):
    task_id: str
    success: bool
    generated_regex: str = ""
    flags: List[str] = Field(default_factory=list)
    explanation: str = ""
    error: Optional[str] = None
