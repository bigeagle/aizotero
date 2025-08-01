"""
PDF解析服务
使用markitdown将PDF转换为Markdown格式
"""

import os

from markitdown import MarkItDown


class PDFParserService:
    """PDF解析服务"""

    def __init__(self):
        self.parser = MarkItDown()

    def parse_pdf(self, pdf_path: str) -> str:
        """
        解析PDF为Markdown

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


# 全局实例
pdf_parser = PDFParserService()
