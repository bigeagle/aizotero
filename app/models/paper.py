from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Paper(BaseModel):
    """论文模型，用于Zotero集成"""

    id: str
    title: str
    authors: str = ""
    year: str | None = None
    journal: str | None = None
    abstract: str | None = None
    doi: str | None = None
    url: str | None = None
    tags: list[str] = Field(default_factory=list)
    pdf_path: str | None = None
    has_pdf: bool = False

    model_config = {"from_attributes": True}


class PaperList(BaseModel):
    """论文列表响应"""

    papers: list[Paper]
    total: int

    model_config = {"from_attributes": True}


class PaperResponse(BaseModel):
    """简化响应模型，用于前端展示"""

    id: str
    title: str
    authors: str = ""
    year: str | None = None
    journal: str | None = None
    abstract: str | None = None
    doi: str | None = None
    url: str | None = None
    tags: list[str] = Field(default_factory=list)
    pdf_path: str | None = None
    has_pdf: bool = False

    model_config = {"from_attributes": True}


class PaperRecord(BaseModel):
    """完整论文记录，包含所有元数据"""

    id: str
    title: str
    authors: str = ""
    year: str | None = None
    journal: str | None = None
    abstract: str | None = None
    doi: str | None = None
    url: str | None = None
    pdf_path: str | None = None
    tags: list[str] = Field(default_factory=list)
    collections: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    notes: str | None = None
    date_added: datetime
    date_modified: datetime
    zotero_key: str
    zotero_version: int
    extra: dict[str, Any] = Field(default_factory=dict)

    model_config = {
        "from_attributes": True,
        "json_encoders": {datetime: lambda v: v.isoformat()},
    }
