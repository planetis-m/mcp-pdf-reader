"""Tests for MCP PDF server."""

import pytest
from pathlib import Path
from mcp_pdf_reader.server import resolve_path


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
