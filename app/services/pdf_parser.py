"""
PDF解析服务
使用markitdown将PDF转换为Markdown格式，通过线程池处理同步操作
包含文件内容缓存功能
"""

import asyncio
import hashlib
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from markitdown import MarkItDown

from app.core.config import settings


class PDFParserService:
    """PDF解析服务"""

    def __init__(self, max_workers: int = 4):
        self.parser = MarkItDown()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # 创建缓存目录
        self.cache_dir = settings.DATA_DIR / "cache" / "markitdown"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, pdf_path: str) -> str:
        """
        生成缓存键

        Args:
            pdf_path: PDF文件路径

        Returns:
            基于文件内容的MD5哈希值
        """
        try:
            with open(pdf_path, "rb") as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            return file_hash
        except Exception:
            # 如果无法读取文件内容，使用文件路径作为备份
            return hashlib.md5(pdf_path.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{cache_key}.md"

    def _is_cached(self, cache_key: str) -> bool:
        """检查是否有缓存"""
        cache_path = self._get_cache_path(cache_key)
        return cache_path.exists()

    def _load_cache(self, cache_key: str) -> str | None:
        """从缓存加载内容"""
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            try:
                return cache_path.read_text(encoding="utf-8")
            except Exception:
                return None
        return None

    def _save_cache(self, cache_key: str, content: str) -> None:
        """保存内容到缓存"""
        cache_path = self._get_cache_path(cache_key)
        try:
            cache_path.write_text(content, encoding="utf-8")
        except Exception:
            # 缓存失败不影响主功能
            pass

    def _parse_pdf_sync(self, pdf_path: str) -> str:
        """
        同步解析PDF为Markdown（内部使用）

        Args:
            pdf_path: PDF文件路径

        Returns:
            Markdown文本内容
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")

        # 检查缓存
        cache_key = self._get_cache_key(pdf_path)
        cached_content = self._load_cache(cache_key)
        if cached_content is not None:
            return cached_content

        # 解析PDF
        try:
            result = self.parser.convert(pdf_path)
            content = result.text_content

            # 保存到缓存
            self._save_cache(cache_key, content)

            return content
        except Exception as e:
            raise RuntimeError(f"PDF解析失败: {str(e)}") from e

    async def parse_pdf(self, pdf_path: str) -> str:
        """
        异步解析PDF为Markdown（使用线程池）

        Args:
            pdf_path: PDF文件路径

        Returns:
            Markdown文本内容
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._parse_pdf_sync, pdf_path)

    def shutdown(self):
        """关闭线程池"""
        self.executor.shutdown(wait=True)


# 全局实例
pdf_parser = PDFParserService()
