"""
PDF解析服务
使用markitdown将PDF转换为Markdown格式，通过线程池处理同步操作
"""

import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from markitdown import MarkItDown


class PDFParserService:
    """PDF解析服务"""

    def __init__(self, max_workers: int = 4):
        self.parser = MarkItDown()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

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

        try:
            result = self.parser.convert(pdf_path)
            return result.text_content
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
