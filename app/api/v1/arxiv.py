from typing import Any

from fastapi import APIRouter

from app.models.arxiv import ArxivPaper
from app.services.arxiv_service import ArxivService

router = APIRouter(prefix="/arxiv", tags=["arxiv"])
arxiv_service = ArxivService()


@router.get("/{arxiv_id}", response_model=ArxivPaper)
async def get_arxiv_paper(arxiv_id: str) -> ArxivPaper:
    """获取arXiv论文元数据"""
    return await arxiv_service.get_arxiv_paper(arxiv_id)


@router.get("/{arxiv_id}/pdf")
async def get_arxiv_pdf(arxiv_id: str):
    """获取arXiv PDF文件内容"""
    from fastapi.responses import FileResponse

    pdf_path = await arxiv_service.get_arxiv_pdf(arxiv_id)
    return FileResponse(pdf_path, media_type="application/pdf")


@router.get("/{arxiv_id}/markdown")
async def get_arxiv_markdown(arxiv_id: str) -> dict[str, Any]:
    """获取arXiv论文的markdown内容"""
    markdown = await arxiv_service.get_arxiv_markdown(arxiv_id)
    return {"arxiv_id": arxiv_id, "markdown": markdown}


@router.get("/{arxiv_id}/info")
async def get_cache_info(arxiv_id: str) -> dict[str, Any]:
    """获取缓存状态信息"""
    return arxiv_service.get_cache_info(arxiv_id)


@router.delete("/{arxiv_id}/cache")
async def clear_cache(arxiv_id: str) -> str:
    """清除特定论文的缓存"""
    arxiv_service.clear_cache(arxiv_id)
    return "缓存已清除"
