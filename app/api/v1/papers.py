from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.models.paper import PaperResponse
from app.services.pdf_parser import pdf_parser
from app.services.zotero_service import ZoteroService

router = APIRouter()
zotero_service = ZoteroService(user_id=0)  # 本地API，user_id为0


@router.get("/papers", response_model=list[PaperResponse])
async def get_papers():
    """获取论文列表（从Zotero）"""
    try:
        papers = zotero_service.get_papers_with_pdfs(limit=100)

        # 转换为PaperResponse模型
        paper_responses = []
        for paper in papers:
            data = paper.get("data", {})
            authors = ""
            if "creators" in data:
                author_names = []
                for creator in data["creators"]:
                    if creator.get("creatorType") == "author":
                        name_parts = []
                        if creator.get("firstName"):
                            name_parts.append(creator["firstName"])
                        if creator.get("lastName"):
                            name_parts.append(creator["lastName"])
                        author_names.append(" ".join(name_parts))
                authors = ", ".join(author_names)

            # 获取PDF附件和URL
            pdf_attachments = paper.get("pdf_attachments", [])
            pdf_url = ""
            if pdf_attachments:
                pdf_url = (
                    zotero_service.get_pdf_file_path(pdf_attachments[0]["key"]) or ""
                )

            paper_responses.append(
                PaperResponse(
                    id=paper.get("key", ""),
                    title=data.get("title", "无标题"),
                    authors=authors,
                    year=data.get("date", ""),
                    journal=data.get("publicationTitle", ""),
                    abstract=data.get("abstractNote", ""),
                    doi=data.get("DOI", ""),
                    url=data.get("url", ""),
                    tags=[tag.get("tag", "") for tag in data.get("tags", [])],
                    pdf_path=pdf_url,
                    has_pdf=len(pdf_attachments) > 0,
                )
            )

        return paper_responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/papers/{paper_id}", response_model=PaperResponse)
async def get_paper(paper_id: str):
    """获取特定论文（从Zotero）"""
    try:
        paper = zotero_service.get_paper_by_key(paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")

        data = paper.get("data", {})
        authors = ""
        if "creators" in data:
            author_names = []
            for creator in data["creators"]:
                if creator.get("creatorType") == "author":
                    name_parts = []
                    if creator.get("firstName"):
                        name_parts.append(creator["firstName"])
                    if creator.get("lastName"):
                        name_parts.append(creator["lastName"])
                    author_names.append(" ".join(name_parts))
            authors = ", ".join(author_names)

        # 获取PDF附件和URL
        pdf_attachments = zotero_service.get_pdf_attachments(paper_id)
        pdf_url = ""
        if pdf_attachments:
            pdf_url = zotero_service.get_pdf_file_path(pdf_attachments[0]["key"]) or ""

        return PaperResponse(
            id=paper.get("key", ""),
            title=data.get("title", "无标题"),
            authors=authors,
            year=data.get("date", ""),
            journal=data.get("publicationTitle", ""),
            abstract=data.get("abstractNote", ""),
            doi=data.get("DOI", ""),
            url=data.get("url", ""),
            tags=[tag.get("tag", "") for tag in data.get("tags", [])],
            pdf_path=pdf_url,
            has_pdf=len(pdf_attachments) > 0,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/papers/search", response_model=list[PaperResponse])
async def search_papers_endpoint(query: str | None = None):
    """搜索论文（从Zotero）"""
    try:
        papers = zotero_service.get_papers_with_pdfs(limit=100)

        if not query:
            # 转换为PaperResponse模型
            paper_responses = []
            for paper in papers:
                data = paper.get("data", {})
                authors = ""
                if "creators" in data:
                    author_names = []
                    for creator in data["creators"]:
                        if creator.get("creatorType") == "author":
                            name_parts = []
                            if creator.get("firstName"):
                                name_parts.append(creator["firstName"])
                            if creator.get("lastName"):
                                name_parts.append(creator["lastName"])
                            author_names.append(" ".join(name_parts))
                    authors = ", ".join(author_names)

                # 获取PDF附件和URL
                pdf_attachments = paper.get("pdf_attachments", [])
                pdf_url = ""
                if pdf_attachments:
                    pdf_url = (
                        zotero_service.get_pdf_file_path(pdf_attachments[0]["key"])
                        or ""
                    )

                paper_responses.append(
                    PaperResponse(
                        id=paper.get("key", ""),
                        title=data.get("title", "无标题"),
                        authors=authors,
                        year=data.get("date", ""),
                        journal=data.get("publicationTitle", ""),
                        abstract=data.get("abstractNote", ""),
                        doi=data.get("DOI", ""),
                        url=data.get("url", ""),
                        tags=[tag.get("tag", "") for tag in data.get("tags", [])],
                        pdf_path=pdf_url,
                        has_pdf=len(pdf_attachments) > 0,
                    )
                )
            return paper_responses

        query_lower = query.lower()
        filtered_papers = []
        for paper in papers:
            data = paper.get("data", {})
            title = data.get("title", "").lower()
            abstract = data.get("abstractNote", "").lower()

            if (
                query_lower in title
                or query_lower in abstract
                or any(
                    query_lower in tag.get("tag", "").lower()
                    for tag in data.get("tags", [])
                )
            ):
                # 转换为PaperResponse模型
                authors = ""
                if "creators" in data:
                    author_names = []
                    for creator in data["creators"]:
                        if creator.get("creatorType") == "author":
                            name_parts = []
                            if creator.get("firstName"):
                                name_parts.append(creator["firstName"])
                            if creator.get("lastName"):
                                name_parts.append(creator["lastName"])
                            author_names.append(" ".join(name_parts))
                    authors = ", ".join(author_names)

                # 获取PDF附件和URL
                pdf_attachments = paper.get("pdf_attachments", [])
                pdf_url = ""
                if pdf_attachments:
                    pdf_url = (
                        zotero_service.get_pdf_file_path(pdf_attachments[0]["key"])
                        or ""
                    )

                filtered_papers.append(
                    PaperResponse(
                        id=paper.get("key", ""),
                        title=data.get("title", "无标题"),
                        authors=authors,
                        year=data.get("date", ""),
                        journal=data.get("publicationTitle", ""),
                        abstract=data.get("abstractNote", ""),
                        doi=data.get("DOI", ""),
                        url=data.get("url", ""),
                        tags=[tag.get("tag", "") for tag in data.get("tags", [])],
                        pdf_path=pdf_url,
                        has_pdf=len(pdf_attachments) > 0,
                    )
                )

        return filtered_papers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/papers/{paper_id}/pdf")
async def get_paper_pdf(paper_id: str):
    """获取论文PDF文件"""
    try:
        # 获取论文详情
        paper = zotero_service.get_paper_by_key(paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")

        # 获取PDF附件
        pdfs = zotero_service.get_pdf_attachments(paper_id)
        if not pdfs:
            raise HTTPException(status_code=404, detail="No PDF found")

        # 获取PDF文件的实际路径
        pdf_url = zotero_service.get_pdf_file_path(pdfs[0]["key"])
        if not pdf_url:
            raise HTTPException(status_code=404, detail="PDF file not accessible")

        # 从file:// URL提取本地文件路径
        if pdf_url.startswith("file://"):
            pdf_file_path = pdf_url.replace("file://", "")
        else:
            pdf_file_path = pdf_url

        # 检查文件是否存在
        import os

        if not os.path.exists(pdf_file_path):
            raise HTTPException(status_code=404, detail="PDF file not found")

        # 直接提供文件服务，而不是重定向
        return FileResponse(pdf_file_path, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/papers/{paper_id}/markdown")
async def get_paper_markdown(paper_id: str):
    """获取论文PDF的Markdown格式内容"""
    # 获取论文详情
    paper = zotero_service.get_paper_by_key(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    # 获取PDF附件
    pdfs = zotero_service.get_pdf_attachments(paper_id)
    if not pdfs:
        raise HTTPException(status_code=404, detail="No PDF found")

    # 获取PDF文件的实际路径
    pdf_url = zotero_service.get_pdf_file_path(pdfs[0]["key"])
    if not pdf_url:
        raise HTTPException(status_code=404, detail="PDF file not accessible")

    # 从本地文件路径读取PDF
    # 提取本地文件路径从file:// URL
    if pdf_url.startswith("file://"):
        pdf_file = pdf_url.replace("file://", "")
    else:
        pdf_file = pdf_url

    pdf_file_path = Path(pdf_file)
    if not pdf_file_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found")

    markdown = pdf_parser.parse_pdf(str(pdf_file_path))
    return {"paper_id": paper_id, "markdown": markdown}


@router.get("/health")
async def health_check():
    return {"status": "ok"}
