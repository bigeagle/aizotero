import requests
from fastapi import HTTPException


class ZoteroService:
    def __init__(self, user_id: int = 0, base_url: str = "http://localhost:23119"):
        self.user_id = user_id
        self.base_url = base_url
        self.session = requests.Session()

    def test_connection(self) -> bool:
        """测试Zotero本地API连接"""
        response = self.session.get(
            f"{self.base_url}/api/users/{self.user_id}/items/top", timeout=5
        )
        return response.status_code == 200

    def get_papers(self, limit: int = 100) -> list[dict]:
        """获取论文列表，按创建时间倒序排序"""
        response = self.session.get(
            f"{self.base_url}/api/users/{self.user_id}/items/top",
            params={
                "format": "json",
                "limit": limit,
                "sort": "dateAdded",
                "direction": "desc",
            },
        )
        response.raise_for_status()
        return response.json()

    def get_paper_by_key(self, key: str) -> dict:
        """根据key获取单篇论文详情"""
        response = self.session.get(
            f"{self.base_url}/api/users/{self.user_id}/items/{key}"
        )
        response.raise_for_status()
        return response.json()

    def get_pdf_attachments(self, item_key: str) -> list[dict]:
        """获取论文的PDF附件"""
        # 获取该论文的子项（attachments）
        response = self.session.get(
            f"{self.base_url}/api/users/{self.user_id}/items/{item_key}/children"
        )
        response.raise_for_status()
        children = response.json()

        # 过滤出PDF附件
        pdf_attachments = []
        for child in children:
            if (
                child.get("data", {}).get("itemType") == "attachment"
                and child.get("data", {}).get("contentType") == "application/pdf"
            ):
                pdf_attachments.append(child)

        return pdf_attachments

    def get_pdf_file_path(self, attachment_key: str) -> str | None:
        """获取PDF文件的实际路径（通过302重定向）"""
        response = self.session.get(
            f"{self.base_url}/api/users/{self.user_id}/items/{attachment_key}/file",
            allow_redirects=False,  # 不要自动跟随重定向
        )

        if response.status_code == 302:
            redirect_url = response.headers.get("Location")
            return redirect_url
        elif response.status_code == 200:
            # 直接返回文件内容，这种情况通常不会发生
            return None
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Unexpected status code: {response.status_code}",
            )

    def get_papers_with_pdfs(self, limit: int = 100) -> list[dict]:
        """获取带有PDF的论文列表"""
        papers = self.get_papers(limit)
        papers_with_pdfs = []

        for paper in papers:
            key = paper.get("key")
            if key:
                # 获取PDF附件
                pdfs = self.get_pdf_attachments(key)
                if pdfs:
                    paper["pdf_attachments"] = pdfs
                    # 获取第一个PDF的路径
                    pdf_path = self.get_pdf_file_path(pdfs[0]["key"])
                    if pdf_path:
                        paper["pdf_path"] = pdf_path
                    papers_with_pdfs.append(paper)

        return papers_with_pdfs
