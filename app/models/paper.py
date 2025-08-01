from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PaperResponse(BaseModel):
    """简化响应模型，用于前端展示"""

    id: str
    title: str
    authors: list[str]
    year: int | None = None
    journal: str | None = None
    abstract: str | None = None

    model_config = {"from_attributes": True}


class PaperRecord(BaseModel):
    """完整论文记录，包含所有元数据"""

    id: str
    title: str
    authors: list[str]
    year: int | None = None
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
