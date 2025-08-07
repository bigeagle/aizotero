from typing import Any

from fastapi import APIRouter

from app.models.arxiv import ArxivPaper
from app.services.arxiv_service import ArxivService
from app.services.zotero_connector import ZoteroConnectorService
from app.services.zotero_service import ZoteroService

router = APIRouter(prefix="/arxiv", tags=["arxiv"])
arxiv_service = ArxivService()
zotero_service = ZoteroService(user_id=0)
zotero_connector = ZoteroConnectorService(
    zotero_service=zotero_service, arxiv_service=arxiv_service
)


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


@router.get("/{arxiv_id}/check-existence")
async def check_arxiv_existence(arxiv_id: str) -> dict[str, Any]:
    """检查arXiv论文是否已存在于Zotero库中"""
    try:
        # 获取arXiv论文元数据
        paper = await arxiv_service.get_arxiv_paper(arxiv_id)
        if not paper:
            return {"exists": False, "message": "arXiv论文未找到"}

        # 检查是否已存在
        existing_item_id = await zotero_connector.find_saved_arxiv_paper(
            arxiv_id, paper.title
        )

        if existing_item_id:
            return {
                "exists": True,
                "item_id": existing_item_id,
                "title": paper.title,
                "message": "论文已存在于Zotero库中",
            }
        else:
            return {
                "exists": False,
                "title": paper.title,
                "message": "论文未存在于Zotero库中",
            }
    except Exception as e:
        return {"exists": False, "error": str(e), "message": "检查失败"}


@router.post("/{arxiv_id}/save-to-zotero")
async def save_arxiv_to_zotero(
    arxiv_id: str, include_pdf: bool = True
) -> dict[str, str]:
    """将arXiv论文保存到Zotero"""
    item_id = await zotero_connector.save_arxiv_paper_to_zotero(
        arxiv_id, include_pdf=include_pdf
    )
    return {"item_id": item_id, "status": "success"}
