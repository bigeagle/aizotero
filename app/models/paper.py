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
