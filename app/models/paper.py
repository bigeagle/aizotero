from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class PaperResponse(BaseModel):
    """简化响应模型，用于前端展示"""
    id: str
    title: str
    authors: List[str]
    year: Optional[int] = None
    journal: Optional[str] = None
    abstract: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class PaperRecord(BaseModel):
    """完整论文记录，包含所有元数据"""
    id: str
    title: str
    authors: List[str]
    year: Optional[int] = None
    journal: Optional[str] = None
    abstract: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    pdf_path: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    collections: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    date_added: datetime
    date_modified: datetime
    zotero_key: str
    zotero_version: int
    extra: Dict[str, Any] = Field(default_factory=dict)

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }