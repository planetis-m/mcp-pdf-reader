"""
MCP PDF Server - Simple PDF text extraction, OCR, and image extraction.
"""

import os
import base64
import logging
from typing import Optional, Dict, Any
from pathlib import Path

import fitz
from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('mcp-pdf-server')

mcp = FastMCP("PDF Reader", version="1.0.0")


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
        end_page: End page (inclusive, default: last page)

    Returns:
        Extracted text with page markers
    """
    path = resolve_path(file_path)
    doc = fitz.open(path)

    total_pages = len(doc)
    start_page = max(1, start_page)
    end_page = min(total_pages, end_page or total_pages)

    if start_page > end_page:
        start_page, end_page = end_page, start_page

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
    dpi: int = 300
) -> str:
    """
    Extract text from PDF using OCR.

    Args:
        file_path: Path to PDF file
        start_page: Start page (1-based, default: 1)
        end_page: End page (inclusive, default: last page)
        language: OCR language code (eng, fra, deu, spa, chi_sim, etc.)
        dpi: Resolution (default: 300, higher = better quality but slower)

    Returns:
        OCR extracted text with page markers
    """
    path = resolve_path(file_path)
    doc = fitz.open(path)

    total_pages = len(doc)
    start_page = max(1, start_page)
    end_page = min(total_pages, end_page or total_pages)

    if start_page > end_page:
        start_page, end_page = end_page, start_page

    result = f"File: {path.name} | Pages: {total_pages}\n"

    for page_num in range(start_page - 1, end_page):
        page = doc[page_num]
        textpage = page.get_textpage_ocr(flags=3, language=language, dpi=dpi, full=True)
        text = page.get_text(textpage=textpage).strip()
        result += f"\n<page n={page_num + 1}>\n{text}\n</page>\n"

    doc.close()
    return result


@mcp.tool()
def read_pdf_images(
    file_path: str,
    page_number: int = 1
) -> Dict[str, Any]:
    """
    Extract images from a PDF page.

    Args:
        file_path: Path to PDF file
        page_number: Page number (1-based, default: 1)

    Returns:
        Dictionary with image metadata and base64-encoded image data
    """
    path = resolve_path(file_path)
    doc = fitz.open(path)

    total_pages = len(doc)
    if page_number < 1 or page_number > total_pages:
        raise ValueError(f"Page {page_number} out of range (1-{total_pages})")

    page = doc[page_number - 1]
    image_list = page.get_images(full=True)

    images = []
    for idx, img in enumerate(image_list):
        xref = img[0]
        base_image = doc.extract_image(xref)

        images.append({
            "image_id": f"p{page_number}_img{idx + 1}",
            "width": base_image["width"],
            "height": base_image["height"],
            "format": base_image["ext"],
            "size_bytes": len(base_image["image"]),
            "base64": base64.b64encode(base_image["image"]).decode('utf-8')
        })

    doc.close()

    return {
        "file": path.name,
        "page": page_number,
        "total_pages": total_pages,
        "image_count": len(images),
        "images": images
    }


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

