# MCP PDF Reader - Usage Examples

## Basic Text Extraction

```python
# Extract all pages
read_pdf_text(file_path="document.pdf")

# Extract specific pages
read_pdf_text(file_path="document.pdf", start_page=1, end_page=5)

# Using relative path (requires PDF_DIR)
read_pdf_text(file_path="reports/annual.pdf")
