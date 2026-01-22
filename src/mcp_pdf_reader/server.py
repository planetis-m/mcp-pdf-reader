"""
MCP PDF Server - Simple PDF text extraction, OCR, and image extraction.
"""

import uuid
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import fitz
from fastmcp import FastMCP
from mcp.types import ImageContent, TextContent

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('mcp-pdf-server')

# Silence FastMCP logging
logging.getLogger('fastmcp').setLevel(logging.ERROR)

mcp = FastMCP("PDF Reader")

def resolve_path(file_path: str) -> Path:
    """Resolve file path, checking PDF_DIR if needed."""
    path = Path(file_path)
    if not path.exists():
        pdf_dir = os.environ.get("PDF_DIR")
        if pdf_dir:
            alt_path = Path(pdf_dir) / file_path
            if alt_path.exists():
                return alt_path
        raise FileNotFoundError(
            f"File not found: {file_path}\n"
            f"Absolute path: {path.resolve()}\n"
            f"Tip: Use absolute path or set PDF_DIR environment variable"
        )
    return path

@mcp.tool()
def read_pdf_text(
    file_path: str,
    start_page: int = 1,
    end_page: Optional[int] = None
) -> str:
    """
    Extract text from PDF file.

    Args:
        file_path: Path to PDF file
        start_page: Start page (1-based, default: 1)
        end_page: End page (inclusive, default: same as start_page for single page extraction)
                  Use end_page=-1 to read to the last page

    Returns:
        Extracted text with page markers
    """
    path = resolve_path(file_path)
    doc = fitz.open(path)

    total_pages = len(doc)
    end_page = start_page if end_page is None else end_page

    # Support end_page=-1 to read to last page
    if end_page == -1:
        end_page = total_pages

    if start_page > end_page:
        start_page, end_page = end_page, start_page

    start_page = max(1, start_page)
    end_page = min(total_pages, end_page)

    result = f"File: {path.name} | Pages: {total_pages}\n"

    for page_num in range(start_page - 1, end_page):
        page = doc[page_num]
        text = page.get_text().strip()
        result += f"\n<page n={page_num + 1}>\n{text}\n</page>\n"

    doc.close()
    return result


@mcp.tool()
def read_by_ocr(
    file_path: str,
    start_page: int = 1,
    end_page: Optional[int] = None,
    language: str = "eng",
    dpi: int = 200
) -> str:
    """
    Extract text from PDF using OCR.

    Args:
        file_path: Path to PDF file
        start_page: Start page (1-based, default: 1)
        end_page: End page (inclusive, default: same as start_page for single page extraction)
                  Use end_page=-1 to read to the last page
        language: OCR language code (eng, fra, deu, spa, chi_sim, etc.)
        dpi: Resolution (default: 200, higher = better quality but slower)

    Returns:
        OCR extracted text with page markers
    """
    path = resolve_path(file_path)
    doc = fitz.open(path)

    total_pages = len(doc)
    end_page = start_page if end_page is None else end_page

    # Support end_page=-1 to read to last page
    if end_page == -1:
        end_page = total_pages

    if start_page > end_page:
        start_page, end_page = end_page, start_page

    start_page = max(1, start_page)
    end_page = min(total_pages, end_page)

    result = f"File: {path.name} | Pages: {total_pages}\n"

    for page_num in range(start_page - 1, end_page):
        page = doc[page_num]
        textpage = page.get_textpage_ocr(flags=16, language=language, dpi=dpi, full=True)
        text = page.get_text(textpage=textpage).strip()
        result += f"\n<page n={page_num + 1}>\n{text}\n</page>\n"

    doc.close()
    return result


@mcp.tool()
def screenshot_pdf_pages(
    file_path: str,
    start_page: int = 1,
    end_page: Optional[int] = None,
    dpi: int = 100
) -> List[Any]:
    """
    Render PDF pages as high-quality screenshots for multimodal analysis.

    Args:
        file_path: Path to PDF file
        start_page: Start page (1-based, default: 1)
        end_page: End page (inclusive, default: same as start_page for single page extraction)
                  Use end_page=-1 to read to the last page
        dpi: Resolution (default: 100)
    """
    path = resolve_path(file_path)
    doc = fitz.open(str(path))
    total_pages = len(doc)

    # Robust Range Checking
    end_page = start_page if end_page is None else end_page

    # Support end_page=-1 to read to last page
    if end_page == -1:
        end_page = total_pages

    if start_page > end_page:
        start_page, end_page = end_page, start_page

    start_page = max(1, start_page)
    end_page = min(total_pages, end_page)

    content_blocks = []

    for page_num in range(start_page - 1, end_page):
        page = doc[page_num]

        # Render page to bytes
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
        img_bytes = pix.tobytes("png")

        # Create the FastMCP Image wrapper
        img_wrapper = Image(data=img_bytes, format="png")
        
        # Reference label block
        content_blocks.append(TextContent(type="text", text=f"<page n={page_num + 1}>\n{text}\n</page>"))
        content_blocks.append(img_wrapper.to_image_content(mime_type="image/png"))

    doc.close()
    return content_blocks


def main():
    """Main entry point for the MCP server."""
    pdf_dir = os.environ.get("PDF_DIR")
    if pdf_dir and Path(pdf_dir).is_dir():
        os.chdir(pdf_dir)
        logger.info(f"Working directory: {pdf_dir}")

    logger.info("Starting MCP PDF Server")
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
