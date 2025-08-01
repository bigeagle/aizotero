from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.data.sample_data import (
    get_paper_by_id,
    get_paper_response_by_id,
    get_sample_papers,
    search_papers,
)
from app.models.paper import PaperRecord, PaperResponse

router = APIRouter()


@router.get("/papers", response_model=list[PaperResponse])
async def get_papers():
    """获取论文列表（简化版）"""
    return get_sample_papers()


@router.get("/papers/records", response_model=list[PaperRecord])
async def get_paper_records():
    """获取完整论文记录列表"""
    from app.data.sample_data import get_sample_records

    return get_sample_records()


@router.get("/papers/{paper_id}", response_model=PaperResponse)
async def get_paper(paper_id: str):
    """获取特定论文（简化版）"""
    paper = get_paper_response_by_id(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.get("/papers/{paper_id}/record", response_model=PaperRecord)
async def get_paper_record(paper_id: str):
    """获取特定论文的完整记录"""

    paper = get_paper_by_id(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.get("/papers/search", response_model=list[PaperResponse])
async def search_papers_endpoint(query: str | None = None):
    """搜索论文（简化版）"""
    if not query:
        return get_sample_papers()
    return search_papers(query)


@router.get("/papers/search/records", response_model=list[PaperRecord])
async def search_paper_records(query: str | None = None):
    """搜索论文并返回完整记录"""
    from app.data.sample_data import get_sample_records

    if not query:
        return get_sample_records()

    query_lower = query.lower()
    return [
        paper
        for paper in get_sample_records()
        if query_lower in paper.title.lower()
        or any(query_lower in author.lower() for author in paper.authors)
        or query_lower in paper.abstract.lower()
        or any(query_lower in tag.lower() for tag in paper.tags)
        or any(query_lower in keyword.lower() for keyword in paper.keywords)
    ]


@router.get("/papers/{paper_id}/pdf")
async def get_paper_pdf(paper_id: str):
    """获取论文PDF文件"""
    from pathlib import Path

    from fastapi.responses import FileResponse

    paper = get_paper_by_id(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    if not paper.pdf_path:
        raise HTTPException(status_code=404, detail="PDF file not available")

    pdf_path = Path(paper.pdf_path)
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "inline; filename*=utf-8''{}.pdf".format(
                paper.title.replace(" ", "_")
            )
        },
    )


@router.get("/papers/{paper_id}/markdown")
async def get_paper_markdown(paper_id: str):
    """获取论文PDF的Markdown格式内容"""
    from app.services.pdf_parser import pdf_parser

    paper = get_paper_by_id(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    if not paper.pdf_path:
        raise HTTPException(status_code=404, detail="PDF file not available")

    pdf_path = Path(paper.pdf_path)
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found")

    try:
        markdown = pdf_parser.parse_pdf(str(pdf_path))
        return {"paper_id": paper_id, "markdown": markdown}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF解析失败: {str(e)}") from e


@router.get("/health")
async def health_check():
    return {"status": "ok"}
