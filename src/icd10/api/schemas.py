from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChapterRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numeral: str
    title_en: str


class BlockRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code_start: str
    code_end: str
    title_en: str


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    kind: Literal["includes", "excludes", "note", "use_additional"]
    text: str


class CodeRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    title_en: str
    level: int


class CodeSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    title_en: str
    level: int
    is_leaf: bool
    dagger: bool
    asterisk: bool
    chapter: ChapterRef | None = None
    block: BlockRef | None = None


class CodeDetail(CodeSummary):
    ancestors: list[CodeRef] = Field(default_factory=list)
    children: list[CodeSummary] = Field(default_factory=list)
    notes: list[NoteOut] = Field(default_factory=list)


class ChapterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numeral: str
    title_en: str
    code_start: str
    code_end: str
    sort_order: int
    notes: list[dict[str, str]] = Field(default_factory=list)
    block_count: int = 0


class BlockOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code_start: str
    code_end: str
    title_en: str
    sort_order: int


class SearchHit(BaseModel):
    code: str
    title_en: str
    level: int
    is_leaf: bool
    score: float
    matched_term: str | None = None


class SearchResponse(BaseModel):
    query: str
    total: int
    limit: int
    offset: int
    items: list[SearchHit]


class PageMeta(BaseModel):
    total: int
    limit: int
    offset: int


class LookupRequest(BaseModel):
    codes: list[str] = Field(min_length=1)


class LookupResponse(BaseModel):
    found: list[CodeSummary]
    not_found: list[str]


class ValidationItem(BaseModel):
    code: str
    valid: bool
    level: int | None = None
    is_leaf: bool | None = None
    parent: CodeRef | None = None
    chapter: ChapterRef | None = None
    reason: str | None = None


class ValidationRequest(BaseModel):
    codes: list[str] = Field(min_length=1)


class ValidationResponse(BaseModel):
    items: list[ValidationItem]


class DatasetMeta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    imported_at: datetime
    status: str
    code_count: int
    meta: dict[str, object]


class MetaResponse(BaseModel):
    api_version: str
    dataset: DatasetMeta | None
    license_notice: str


class Problem(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None


class CaseLineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role: str
    diagnosis_text: str
    code: str | None
    code_title_en: str | None
    code_status: str


class CaseExampleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    example_no: str
    page: int | None
    scenario_th: str
    lines: list[CaseLineOut] = Field(default_factory=list)


class CaseExampleList(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[CaseExampleOut]
