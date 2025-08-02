from fastapi import APIRouter, HTTPException

from app.models.paper import Paper, PaperList
from app.services.zotero_service import ZoteroService

router = APIRouter(prefix="/zotero", tags=["zotero"])

zotero_service = ZoteroService(user_id=0)  # 本地API，user_id为0


@router.get("/test")
async def test_zotero_connection():
    """测试Zotero本地API连接"""
    try:
        is_connected = zotero_service.test_connection()
        return {"connected": is_connected}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/papers", response_model=PaperList)
async def get_papers(limit: int = 50):
    """获取Zotero论文列表"""
    try:
        papers = zotero_service.get_papers_with_pdfs(limit=limit)

        # 转换为我们的Paper模型
        paper_list = []
        for paper in papers:
            data = paper.get("data", {})
            paper_obj = Paper(
                id=paper.get("key", ""),
                title=data.get("title", "无标题"),
                authors=", ".join(data.get("creators", [])),
                abstract=data.get("abstractNote", ""),
                year=data.get("date", ""),
                journal=data.get("publicationTitle", ""),
                doi=data.get("DOI", ""),
                url=data.get("url", ""),
                tags=[tag.get("tag", "") for tag in data.get("tags", [])],
                pdf_path=paper.get("pdf_path", ""),
                has_pdf=len(paper.get("pdf_attachments", [])) > 0,
            )
            paper_list.append(paper_obj)

        return PaperList(papers=paper_list, total=len(paper_list))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/papers/{paper_key}", response_model=Paper)
async def get_paper(paper_key: str):
    """获取单篇论文详情"""
    try:
        paper = zotero_service.get_paper_by_key(paper_key)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")

        data = paper.get("data", {})
        return Paper(
            id=paper.get("key", ""),
            title=data.get("title", "无标题"),
            authors=", ".join(data.get("creators", [])),
            abstract=data.get("abstractNote", ""),
            year=data.get("date", ""),
            journal=data.get("publicationTitle", ""),
            doi=data.get("DOI", ""),
            url=data.get("url", ""),
            tags=[tag.get("tag", "") for tag in data.get("tags", [])],
            pdf_path=paper.get("pdf_path", ""),
            has_pdf=len(paper.get("pdf_attachments", [])) > 0,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/papers/{paper_key}/pdf-url")
async def get_pdf_url(paper_key: str):
    """获取PDF文件的服务器URL"""
    try:
        # 获取PDF附件
        pdfs = zotero_service.get_pdf_attachments(paper_key)
        if not pdfs:
            raise HTTPException(status_code=404, detail="No PDF found")

        # 获取第一个PDF的路径
        pdf_path = zotero_service.get_pdf_file_path(pdfs[0]["key"])
        if not pdf_path:
            raise HTTPException(status_code=404, detail="PDF file not found")

        # 返回本地文件URL
        return {"pdf_url": f"/api/v1/zotero/pdfs/{paper_key}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
