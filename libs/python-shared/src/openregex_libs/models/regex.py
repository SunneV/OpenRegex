from pydantic import BaseModel, Field, field_validator
from typing import Any, List, Optional


class CheatSheetItem(BaseModel):
    character: str
    description: str


class CheatSheetCategory(BaseModel):
    category: str
    items: List[CheatSheetItem] = Field(default_factory=list)


class EngineDocs(BaseModel):
    trivia: List[str] = Field(default_factory=list)
    cheat_sheet_url: str


class EngineFlag(BaseModel):
    name: str
    description: str
    group: str


class EngineCapabilities(BaseModel):
    flags: List[EngineFlag] = Field(default_factory=list)
    supports_lookaround: bool
    supports_backrefs: bool

    @field_validator("flags", mode="before")
    @classmethod
    def _normalize_legacy_flags(cls, value: Any) -> Any:
        if value is None:
            return []
        if not isinstance(value, list):
            return value
        normalized: List[Any] = []
        for item in value:
            if isinstance(item, str):
                normalized.append(
                    {
                        "name": item,
                        "description": f"Flag ({item})",
                        "group": "Basic",
                    }
                )
            else:
                normalized.append(item)
        return normalized


class EngineExample(BaseModel):
    regex: str
    text: str


class EngineInfo(BaseModel):
    engine_id: str
    engine_language_type: str
    engine_language_version: str
    engine_regex_lib: str
    engine_regex_lib_version: str
    engine_label: str
    engine_capabilities: EngineCapabilities
    engine_docs: EngineDocs
    engine_cheat_sheet: List[CheatSheetCategory] = Field(default_factory=list)
    engine_examples: List[EngineExample] = Field(default_factory=list)


class WorkerInfo(BaseModel):
    worker_name: str
    worker_version: str
    worker_release_date: str
    engines: List[EngineInfo] = Field(default_factory=list)


class MatchRequest(BaseModel):
    task_id: str = ""
    engine_id: str
    regex: str
    text: str
    flags: List[str] = Field(default_factory=list)


class MatchGroup(BaseModel):
    group_id: int
    name: Optional[str] = None
    content: str
    start: int
    end: int


class MatchItem(BaseModel):
    match_id: int
    full_match: str
    start: int
    end: int
    groups: List[MatchGroup] = Field(default_factory=list)


class MatchResult(BaseModel):
    task_id: str
    engine_id: str
    success: bool
    matches: List[MatchItem] = Field(default_factory=list)
    execution_time_ms: float
    error: Optional[str] = None
