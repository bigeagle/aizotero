from pydantic import BaseModel, Field


class ArxivMetadata(BaseModel):
    """arXiv论文元数据模型"""

    arxiv_id: str
    title: str
    authors: list[str] = Field(default_factory=list)
    abstract: str = ""
    published: str = ""
    categories: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ArxivPaper(BaseModel):
    """arXiv论文完整模型"""

    id: str  # arxiv_id
    title: str
    authors: str = ""
    year: str | None = None
    journal: str | None = None
    abstract: str = ""
    doi: str | None = None
    url: str | None = None
    tags: list[str] = Field(default_factory=list)
    pdf_path: str | None = None
    has_pdf: bool = True

    model_config = {"from_attributes": True}

    @classmethod
    def from_arxiv_metadata(
        cls, metadata: ArxivMetadata, pdf_path: str
    ) -> "ArxivPaper":
        """从arXiv元数据创建模型"""
        return cls(
            id=metadata.arxiv_id,
            title=metadata.title,
            authors=", ".join(metadata.authors),
            year=(
                metadata.published[:4] if metadata.published else None
            ),  # 从ISO日期提取年份
            abstract=metadata.abstract,
            url=f"https://arxiv.org/abs/{metadata.arxiv_id}",
            tags=metadata.categories,
            pdf_path=pdf_path,
            has_pdf=True,
        )
