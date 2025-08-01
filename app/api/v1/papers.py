from fastapi import APIRouter, HTTPException
from typing import List

from app.models.paper import PaperResponse

router = APIRouter()

@router.get("/papers", response_model=List[PaperResponse])
async def get_papers():
    """获取Zotero中的论文列表"""
    return [
        PaperResponse(
            id="sample-1",
            title="示例论文：深度学习的未来",
            authors=["张三", "李四"],
            year=2024,
            journal="Nature AI",
            abstract="这是一个示例论文摘要..."
        )
    ]

@router.get("/health")
async def health_check():
    return {"status": "ok"}