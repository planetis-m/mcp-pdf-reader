"""Tests for MCP PDF server."""


import fitz  # PyMuPDF
import pytest

from mcp_pdf_reader.server import read_by_ocr, read_pdf_text, resolve_path


@pytest.fixture
def test_pdf(tmp_path):
    """Create a test PDF with 5 pages."""
    pdf_path = tmp_path / "test.pdf"
    doc = fitz.open()

    # Create 5 pages with distinct content
    for i in range(1, 6):
        page = doc.new_page()
        page.insert_text((72, 72), f"This is page {i}")

    doc.save(pdf_path)
    doc.close()
    return pdf_path


def test_resolve_path_exists(tmp_path):
    """Test path resolution for existing file."""
    test_file = tmp_path / "test.pdf"
    test_file.touch()

    resolved = resolve_path(str(test_file))
    assert resolved == test_file


def test_resolve_path_not_exists():
    """Test path resolution for non-existing file."""
    with pytest.raises(FileNotFoundError):
        resolve_path("nonexistent.pdf")


def test_read_pdf_text_single_page_default(test_pdf):
    """Test reading a single page when end_page is not specified."""
    result = read_pdf_text.fn(str(test_pdf), start_page=3)

    # Should only contain page 3
    assert "<page n=3>" in result
    assert "This is page 3" in result

    # Should not contain other pages
    assert "<page n=2>" not in result
    assert "<page n=4>" not in result


def test_read_pdf_text_page_range(test_pdf):
    """Test reading a range of pages."""
    result = read_pdf_text.fn(str(test_pdf), start_page=2, end_page=4)

    # Should contain pages 2, 3, 4
    assert "<page n=2>" in result
    assert "<page n=3>" in result
    assert "<page n=4>" in result
    assert "This is page 2" in result
    assert "This is page 3" in result
    assert "This is page 4" in result

    # Should not contain pages 1 and 5
    assert "<page n=1>" not in result
    assert "<page n=5>" not in result


def test_read_pdf_text_to_last_page(test_pdf):
    """Test reading from a page to the last page using end_page=-1."""
    result = read_pdf_text.fn(str(test_pdf), start_page=3, end_page=-1)

    # Should contain pages 3, 4, 5
    assert "<page n=3>" in result
    assert "<page n=4>" in result
    assert "<page n=5>" in result
    assert "This is page 3" in result
    assert "This is page 4" in result
    assert "This is page 5" in result

    # Should not contain pages 1 and 2
    assert "<page n=1>" not in result
    assert "<page n=2>" not in result


def test_read_pdf_text_first_page_default(test_pdf):
    """Test reading the first page when only start_page=1."""
    result = read_pdf_text.fn(str(test_pdf), start_page=1)

    # Should only contain page 1
    assert "<page n=1>" in result
    assert "This is page 1" in result

    # Should not contain other pages
    assert "<page n=2>" not in result
    assert "<page n=3>" not in result


def test_read_by_ocr_single_page_default(test_pdf):
    """Test OCR reading a single page when end_page is not specified."""
    result = read_by_ocr.fn(str(test_pdf), start_page=3)

    # Should only contain page 3
    assert "<page n=3>" in result
    assert "This is page 3" in result

    # Should not contain other pages
    assert "<page n=2>" not in result
    assert "<page n=4>" not in result


def test_read_by_ocr_page_range(test_pdf):
    """Test OCR reading a range of pages."""
    result = read_by_ocr.fn(str(test_pdf), start_page=2, end_page=4)

    # Should contain pages 2, 3, 4
    assert "<page n=2>" in result
    assert "<page n=3>" in result
    assert "<page n=4>" in result

    # Should not contain pages 1 and 5
    assert "<page n=1>" not in result
    assert "<page n=5>" not in result


def test_read_by_ocr_to_last_page(test_pdf):
    """Test OCR reading from a page to the last page using end_page=-1."""
    result = read_by_ocr.fn(str(test_pdf), start_page=4, end_page=-1)

    # Should contain pages 4, 5
    assert "<page n=4>" in result
    assert "<page n=5>" in result

    # Should not contain pages 1, 2, 3
    assert "<page n=1>" not in result
    assert "<page n=2>" not in result
    assert "<page n=3>" not in result

