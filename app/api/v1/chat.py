from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.services.database import ChatDatabase

router = APIRouter(prefix="/chat")
chat_db = ChatDatabase()


@router.get("/{paper_id}")
async def get_paper_chat(paper_id: str):
    """获取论文的聊天记录"""
    chat_data = await chat_db.get_chat(paper_id)
    return {"paper_id": paper_id, "chat": chat_data}


@router.post("/{paper_id}")
async def save_paper_chat(paper_id: str, chat_data: List[Dict[str, Any]]):
    """保存论文的聊天记录"""
    await chat_db.save_chat(paper_id, chat_data)
    return {"paper_id": paper_id, "status": "saved"}


@router.delete("/{paper_id}")
async def delete_paper_chat(paper_id: str):
    """删除论文的聊天记录"""
    await chat_db.delete_chat(paper_id)
    return {"paper_id": paper_id, "status": "deleted"}
