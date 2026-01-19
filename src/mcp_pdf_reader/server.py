"""
MCP PDF Server - Simple PDF text extraction, OCR, and image extraction.
"""

import uuid
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import fitz
from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('mcp-pdf-server')

# Setup Resource Directory
PDF_DIR = os.environ.get("PDF_DIR", os.path.join(os.getcwd(), "pdf_resources"))
os.makedirs(PDF_DIR, exist_ok=True)

mcp = FastMCP("PDF Reader", version="1.0.0")

def resolve_path(file_path: str) -> Path:
    """Resolve file path, checking PDF_DIR if needed."""
    path = Path(file_path)
    if not path.exists():
        alt_path = Path(PDF_DIR) / file_path
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
    dpi: int = 200
) -> Dict[str, Any]:
    """
    Render PDF pages as high-quality images (screenshots).
    Use this when the AI needs to 'see' the full layout, text, and diagrams together.

    Args:
        file_path: Path to PDF file
        start_page: Start page (1-based, default: 1)
        end_page: End page (inclusive, default: same as start_page)
                  Use end_page=-1 to read to the last page
        dpi: Resolution (default: 200). 

    Returns:
        Dict containing file metadata and a list of pages with their local image paths.
    """
    path = resolve_path(file_path)
    doc = fitz.open(path)

    total_pages = len(doc)
    end_page = start_page if end_page is None else end_page

    # Robust Range Checking
    if end_page == -1:
        end_page = total_pages

    if start_page > end_page:
        start_page, end_page = end_page, start_page

    start_page = max(1, start_page)
    end_page = min(total_pages, end_page)

    pages_data = []

    for page_num in range(start_page - 1, end_page):
        page = doc[page_num]
        
        # Render the entire page (screenshot)
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
        
        # Generate unique filename
        filename = f"{path.stem}_p{page_num+1}_{uuid.uuid4().hex[:6]}.png"
        save_path = os.path.join(PDF_DIR, filename)
        pix.save(save_path)

        pages_data.append({
            "page_number": page_num + 1,
            "local_path": save_path,
            "dpi": dpi,
            "format": "png"
        })

    doc.close()

    return {
        "file": path.name,
        "total_pages": total_pages,
        "rendered_count": len(pages_data),
        "pages": pages_data,
        "note": "Full page screenshots saved. Use the local_path to read and analyze images."
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
