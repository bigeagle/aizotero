"""
Zotero Connector API 服务
处理与Zotero Connector的通信，实现论文保存功能
"""

import asyncio
import json
import random
import string

import aiohttp
from fastapi import HTTPException

from app.services.arxiv_service import ArxivService
from app.services.zotero_service import ZoteroService


class ZoteroConnectorService:
    """Zotero Connector API 服务类"""

    def __init__(
        self,
        zotero_service: ZoteroService,
        arxiv_service: ArxivService,
        base_url: str = "http://127.0.0.1:23119",
    ):
        self.base_url = base_url
        self.zotero_service = zotero_service
        self.arxiv_service = arxiv_service

    def get_session(self) -> aiohttp.ClientSession:
        """获取配置好的aiohttp会话"""
        return aiohttp.ClientSession(
            base_url=self.base_url,
            timeout=aiohttp.ClientTimeout(total=30),
        )

    async def test_connection(self) -> bool:
        """测试Zotero Connector连接"""
        async with self.get_session() as session:
            try:
                async with session.get(
                    "/connector/ping",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as response:
                    return response.status == 200
            except Exception:
                return False

    def _generate_item_id(self) -> str:
        """生成符合Zotero要求的8位item ID"""
        chars = string.ascii_uppercase + string.digits
        # 第一位必须是字母
        item_id = random.choice(string.ascii_uppercase)
        # 其余7位可以是字母或数字
        item_id += "".join(random.choices(chars, k=7))
        return item_id

    async def save_arxiv_paper_with_attachment(
        self,
        arxiv_id: str,
        title: str,
        authors: list[str],
        abstract: str,
        date: str,
        pdf_path: str | None = None,
    ) -> str | None:
        """保存arXiv论文到Zotero，可选添加PDF附件"""
        # 检查Zotero连接
        if not await self.test_connection():
            raise HTTPException(
                status_code=503,
                detail="Zotero Connector not available. Please start Zotero and ensure the connector is enabled.",
            )

        # 生成共享的sessionID
        session_id = f"aizotero-{arxiv_id}"

        # 验证日期格式
        validated_date = self._validate_date(date)

        # 生成item_id并存储用于附件
        item_id = self._generate_item_id()

        # 保存主条目
        zotero_item = {
            "itemType": "preprint",
            "id": item_id,
            "title": title,
            "creators": self._process_authors(authors),
            "abstractNote": abstract,
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "publisher": "arXiv",
            "archiveID": f"arXiv:{arxiv_id}",
            "DOI": f"10.48550/arXiv.{arxiv_id}",
            "extra": f"arXiv:{arxiv_id}",
        }

        # 只有在日期有效时才添加date字段
        if validated_date:
            zotero_item["date"] = validated_date

        payload = {"items": [zotero_item], "sessionID": session_id}

        async with self.get_session() as session:
            async with session.post(
                "/connector/saveItems",
                json=payload,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 201:
                    _ = await response.json()
                else:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Failed to save item: {error_text}",
                    )

        # 如果有PDF路径，添加附件 - 使用生成的item_id作为parent_key
        if pdf_path:
            await self._save_attachment_with_session(
                parent_item_key=item_id,
                pdf_url=f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                pdf_path=pdf_path,
                filename=f"{arxiv_id}.pdf",
                session_id=session_id,
            )

        return item_id

    def _validate_date(self, date_str: str) -> str | None:
        from datetime import datetime

        """验证并返回格式化的日期，无效返回None"""
        if not date_str or not date_str.strip():
            return None

        date_str = date_str.strip()

        # 尝试匹配 YYYY-MM-DD 格式
        import re

        match = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", date_str)
        if match:
            year, month, day = match.groups()
            try:
                # 验证是否为有效日期
                from datetime import datetime

                datetime(int(year), int(month), int(day))
                return date_str
            except ValueError:
                return None

        # 尝试提取前10个字符（可能包含时间部分）
        if len(date_str) >= 10:
            date_part = date_str[:10]
            match = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", date_part)
            if match:
                year, month, day = match.groups()
                try:
                    datetime(int(year), int(month), int(day))
                    return date_part
                except ValueError:
                    return None

        return None

    def _process_authors(self, authors: list[str]) -> list[dict[str, str]]:
        """处理作者信息"""
        creators = []
        for author in authors:
            parts = author.strip().split(" ", 1)
            if len(parts) == 2:
                creators.append(
                    {
                        "creatorType": "author",
                        "firstName": parts[0],
                        "lastName": parts[1],
                    }
                )
            else:
                # 单名作者或公司名
                creators.append({"creatorType": "author", "name": parts[0]})
        return creators

    async def _save_attachment_with_session(
        self,
        parent_item_key: str,
        pdf_url: str,
        pdf_path: str,
        filename: str,
        session_id: str,
    ) -> None:
        """使用共享sessionID保存附件"""
        # 读取PDF文件内容
        try:
            with open(pdf_path, "rb") as f:
                pdf_content = f.read()
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Failed to read PDF file: {str(e)}"
            ) from e

        # 构建metadata header
        metadata = {
            "parentItemID": parent_item_key,
            "url": pdf_url,
            "title": filename,
            "sessionID": session_id,
        }

        async with self.get_session() as session:
            async with session.post(
                "/connector/saveAttachment",
                headers={
                    "X-Metadata": json.dumps(metadata, ensure_ascii=False),
                    "Content-Type": "application/pdf",
                },
                data=pdf_content,
            ) as response:
                if response.status == 201:
                    _ = await response.text()
                    return
                else:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Failed to save attachment: {error_text}",
                    )

    async def find_saved_arxiv_paper(self, arxiv_id: str, title: str) -> str | None:
        """
        通过arXiv ID和标题查找已保存的论文

        Args:
            arxiv_id: arXiv论文ID
            title: 论文标题

        Returns:
            已保存论文的item_id，如果未找到返回None
        """
        # 使用标题进行搜索
        papers = await self.zotero_service.get_papers(
            q=title[:60], limit=10  # 用标题前60字符搜索
        )

        # 查找匹配的论文
        for paper in papers:
            data = paper.get("data", {})
            url = data.get("url", "")
            if f"arxiv.org/abs/{arxiv_id}" in url:
                return paper.get("key")

        return None

    async def save_arxiv_paper_to_zotero(
        self, arxiv_id: str, include_pdf: bool = True
    ) -> str:
        """
        将arXiv论文保存到Zotero的完整流程

        Args:
            arxiv_id: arXiv论文ID
            include_pdf: 是否包含PDF附件

        Returns:
            保存成功的实际item_id（通过搜索获取）
        """
        # 1. 检查Zotero是否可用
        if not await self.test_connection():
            raise HTTPException(
                status_code=503,
                detail="Zotero Connector not available. Please start Zotero to save papers.",
            )

        # 2. 获取arXiv论文元数据
        metadata = await self.arxiv_service.get_arxiv_metadata(arxiv_id)
        if not metadata:
            raise HTTPException(
                status_code=404, detail=f"arXiv paper '{arxiv_id}' not found"
            )

        # 3. 检查是否已存在
        existing_item_id = await self.find_saved_arxiv_paper(arxiv_id, metadata.title)
        if existing_item_id:
            return existing_item_id

        # 4. 保存到Zotero
        pdf_path = None
        if include_pdf:
            try:
                pdf_path = await self.arxiv_service.get_arxiv_pdf(arxiv_id)
            except Exception:
                # PDF获取失败不影响主功能，继续保存主条目
                pdf_path = None

        await self.save_arxiv_paper_with_attachment(
            arxiv_id=arxiv_id,
            title=metadata.title,
            authors=metadata.authors,
            abstract=metadata.abstract,
            date=metadata.published,
            pdf_path=pdf_path,
        )

        # 5. 搜索实际保存的item
        await asyncio.sleep(2)  # 给Zotero处理时间

        # 6. 获取实际保存的item_id
        saved_item_id = await self.find_saved_arxiv_paper(arxiv_id, metadata.title)
        if saved_item_id:
            return saved_item_id

        raise HTTPException(
            status_code=404,
            detail=f"Could not locate saved paper '{metadata.title}' in Zotero",
        )
