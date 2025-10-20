# MCP PDF Reader

A Model Context Protocol (MCP) server for comprehensive PDF operations including text extraction, OCR, and image processing.

## Features

- **Text Extraction**: Extract text from PDF files with page-level granularity
- **OCR Support**: Extract text from scanned PDFs using Optical Character Recognition
- **Image Extraction**: Extract and encode images from PDF pages
- **Flexible Path Resolution**: Support for absolute paths and PDF_DIR environment variable

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd mcp-pdf-reader

# Install dependencies with uv
uv sync

# Optional: Set PDF directory
cp .env.example .env
# Edit .env and set PDF_DIR=/path/to/your/pdfs
```

### MCP Client Configuration

```json
{
  "mcpServers": {
    "pdf-reader": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/planetis-m/mcp-pdf-reader.git",
        "mcp-pdf-reader"
      ],
      "env": {
        "PDF_DIR": "/path/to/your/pdfs"
      }
    }
  }
}
```

