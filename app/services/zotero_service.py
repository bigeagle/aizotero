import aiohttp
from fastapi import HTTPException


class ZoteroService:
    def __init__(self, user_id: int = 0, base_url: str = "http://localhost:23119"):
        self.user_id = user_id
        self.base_url = base_url

    async def test_connection(self) -> bool:
        """测试Zotero本地API连接"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/api/users/{self.user_id}/items/top",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as response:
                    return response.status == 200
            except Exception:
                return False

    async def get_papers(
        self, limit: int = 100, q: str | None = None, tag: str | None = None
    ) -> list[dict]:
        """获取论文列表，按创建时间倒序排序"""
        params = {
            "format": "json",
            "limit": limit,
            "sort": "dateAdded",
            "direction": "desc",
        }
        if q:
            params["q"] = q
        if tag:
            params["tag"] = tag

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/users/{self.user_id}/items/top",
                params=params,
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def get_paper_by_key(self, key: str) -> dict:
        """根据key获取单篇论文详情"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/users/{self.user_id}/items/{key}"
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def get_pdf_attachments(self, item_key: str) -> list[dict]:
        """获取论文的PDF附件"""
        # 获取该论文的子项（attachments）
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/users/{self.user_id}/items/{item_key}/children"
            ) as response:
                response.raise_for_status()
                children = await response.json()

                # 过滤出PDF附件
                pdf_attachments = []
                for child in children:
                    if (
                        child.get("data", {}).get("itemType") == "attachment"
                        and child.get("data", {}).get("contentType")
                        == "application/pdf"
                    ):
                        pdf_attachments.append(child)

                return pdf_attachments

    async def get_pdf_file_path(self, attachment_key: str) -> str | None:
        """获取PDF文件的实际路径（通过302重定向）"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/users/{self.user_id}/items/{attachment_key}/file",
                allow_redirects=False,  # 不要自动跟随重定向
            ) as response:
                if response.status == 302:
                    redirect_url = response.headers.get("Location")
                    return redirect_url
                elif response.status == 200:
                    # 直接返回文件内容，这种情况通常不会发生
                    return None
                else:
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Unexpected status code: {response.status}",
                    )

    async def get_papers_with_pdfs(
        self, limit: int = 100, q: str | None = None, tag: str | None = None
    ) -> list[dict]:
        """获取带有PDF的论文列表"""
        papers = await self.get_papers(limit, q, tag)
        papers_with_pdfs = []

        for paper in papers:
            key = paper.get("key")
            if key:
                # 获取PDF附件
                pdfs = await self.get_pdf_attachments(key)
                if pdfs:
                    paper["pdf_attachments"] = pdfs
                    # 获取第一个PDF的路径
                    pdf_path = await self.get_pdf_file_path(pdfs[0]["key"])
                    if pdf_path:
                        paper["pdf_path"] = pdf_path
                    papers_with_pdfs.append(paper)

        return papers_with_pdfs
