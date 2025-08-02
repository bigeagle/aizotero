import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import aiohttp

from app.core.config import settings
from app.models.arxiv import ArxivMetadata, ArxivPaper
from app.services.pdf_parser import pdf_parser

logger = logging.getLogger(__name__)


class ArxivService:
    def __init__(self):
        self.base_url = "https://arxiv.org"
        self.pdf_cache_dir = settings.DATA_DIR / "cache" / "arxiv" / "pdf"
        self.metadata_cache_dir = settings.DATA_DIR / "cache" / "arxiv" / "metadata"

        # 确保缓存目录存在
        self.pdf_cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_cache_dir.mkdir(parents=True, exist_ok=True)

        self.pdf_parser = pdf_parser

    async def get_arxiv_paper(self, arxiv_id: str) -> ArxivPaper:
        """获取arXiv论文完整数据"""
        metadata = await self._get_metadata(arxiv_id)
        if not metadata:
            raise ValueError(f"无法获取论文 {arxiv_id} 的元数据")

        # 确保PDF已下载以获取正确路径
        pdf_path = await self._get_pdf(arxiv_id)

        return ArxivPaper.from_arxiv_metadata(metadata, str(pdf_path.absolute()))

    async def get_arxiv_pdf(self, arxiv_id: str) -> str:
        """获取arXiv PDF文件路径，带缓存"""
        pdf_path = await self._get_pdf(arxiv_id)
        return str(pdf_path)

    async def get_arxiv_markdown(self, arxiv_id: str) -> str:
        """获取arXiv论文的markdown内容"""
        # 首先确保PDF已下载
        pdf_path = await self._get_pdf(arxiv_id)
        # 使用pdf_parser的缓存机制转换为markdown
        return await self._get_markdown(pdf_path)

    async def _get_metadata(self, arxiv_id: str) -> ArxivMetadata | None:
        """获取论文元数据，带缓存"""
        cache_file = self.metadata_cache_dir / f"{arxiv_id}.json"

        # 检查缓存
        if cache_file.exists():
            try:
                with open(cache_file, encoding="utf-8") as f:
                    cached_data = json.load(f)

                # 检查缓存是否过期（24小时）
                cached_time = datetime.fromisoformat(
                    cached_data.get("_cached_at", "1970-01-01")
                )
                if datetime.now() - cached_time < timedelta(hours=24):
                    cached_data.pop("_cached_at", None)
                    return ArxivMetadata.model_validate(cached_data)

            except Exception as e:
                logger.warning(f"读取缓存元数据失败: {e}")

        # 从arXiv API获取
        metadata = await self._fetch_metadata(arxiv_id)
        if metadata:
            # 保存缓存
            metadata_dict = metadata.model_dump()
            metadata_with_time = {
                **metadata_dict,
                "_cached_at": datetime.now().isoformat(),
            }
            try:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(metadata_with_time, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.warning(f"保存元数据缓存失败: {e}")

        return metadata

    async def _fetch_metadata(self, arxiv_id: str) -> ArxivMetadata | None:
        """从arXiv API获取元数据"""
        url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                content = await response.text()

        import xml.etree.ElementTree as ET

        root = ET.fromstring(content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        entry = root.find("atom:entry", ns)
        if entry is None:
            return None

        # 提取元数据
        title = entry.find("atom:title", ns)
        authors = entry.findall("atom:author/atom:name", ns) or []
        summary = entry.find("atom:summary", ns)
        published = entry.find("atom:published", ns)

        # 提取分类
        categories = []
        for category in entry.findall("atom:category", ns):
            if "term" in category.attrib:
                categories.append(category.attrib["term"])

        return ArxivMetadata(
            arxiv_id=arxiv_id,
            title=(
                title.text.strip()
                if title is not None and title.text is not None
                else ""
            ),
            authors=[author.text or "" for author in authors],
            abstract=(
                summary.text.strip()
                if summary is not None and summary.text is not None
                else ""
            ),
            published=(
                published.text
                if published is not None and published.text is not None
                else ""
            ),
            categories=categories,
        )

    async def _get_pdf(self, arxiv_id: str) -> Path:
        """获取PDF文件，带缓存"""
        cache_file = self.pdf_cache_dir / f"{arxiv_id}.pdf"

        # 检查缓存
        if cache_file.exists():
            # 验证文件完整性
            if cache_file.stat().st_size > 0:
                return cache_file
            else:
                # 缓存文件损坏，重新下载
                cache_file.unlink(missing_ok=True)

        # 下载PDF
        pdf_url = f"{self.base_url}/pdf/{arxiv_id}.pdf"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(pdf_url) as response:
                    if response.status != 200:
                        raise ValueError(f"无法下载PDF: HTTP {response.status}")

                    # 写入缓存
                    with open(cache_file, "wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)

                    logger.info(f"PDF已缓存: {cache_file}")
                    return cache_file

        except Exception as e:
            logger.error(f"下载PDF失败: {e}")
            raise

    async def _get_markdown(self, pdf_path: Path) -> str:
        """获取markdown内容，使用pdf_parser的缓存"""
        return await self.pdf_parser.parse_pdf(str(pdf_path))

    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()[:8]  # 取前8位作为短哈希

    def get_cache_info(self, arxiv_id: str) -> dict[str, Any]:
        """获取缓存信息"""
        pdf_file = self.pdf_cache_dir / f"{arxiv_id}.pdf"
        metadata_file = self.metadata_cache_dir / f"{arxiv_id}.json"

        info = {
            "pdf_cached": pdf_file.exists(),
            "metadata_cached": metadata_file.exists(),
            "pdf_size": 0,
            "cache_age_hours": 0,
        }

        if pdf_file.exists():
            info["pdf_size"] = pdf_file.stat().st_size

        if metadata_file.exists():
            try:
                with open(metadata_file) as f:
                    cached_data = json.load(f)
                    cached_time = datetime.fromisoformat(
                        cached_data.get("_cached_at", "1970-01-01")
                    )
                    info["cache_age_hours"] = (
                        datetime.now() - cached_time
                    ).total_seconds() / 3600
            except Exception:
                pass

        return info

    def clear_cache(self, arxiv_id: str) -> bool:
        """清除特定论文的缓存"""
        try:
            pdf_file = self.pdf_cache_dir / f"{arxiv_id}.pdf"
            metadata_file = self.metadata_cache_dir / f"{arxiv_id}.json"

            pdf_file.unlink(missing_ok=True)
            metadata_file.unlink(missing_ok=True)

            return True
        except Exception as e:
            logger.error(f"清除缓存失败: {e}")
            return False
