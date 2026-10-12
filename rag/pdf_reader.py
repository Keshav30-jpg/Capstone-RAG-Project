import pymupdf

MAX_FILE_SIZE_MB = 15
MAX_PAGES = 200


class PDFError(Exception):
    """Raised for any problem reading a PDF, so app.py can show a friendly message."""
    pass


def extract_pages(file_bytes: bytes, filename: str) -> list[tuple[int, str]]:
    """
    Extract text from a PDF, page by page.

    A list of (page_number, text) tuples. page_number starts at 1
    (humans don't count from 0), and pages with no extractable text
    are skipped.

    PDFError: if the file is too large, has too many pages, is corrupt,
    or has no extractable text at all.
    """
    # Guardrail 1:
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise PDFError(
            f"'{filename}' is {size_mb:.1f} MB, which exceeds the {MAX_FILE_SIZE_MB} MB limit."
        )

    # pymupdf.open() can take raw bytes directly via stream=, no need to save to disk first.
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        # Corrupt or non-PDF files land here.
        raise PDFError(f"'{filename}' could not be opened. It may be corrupted.") from e

    ## Guardrail 2:
    if doc.page_count > MAX_PAGES:
        doc.close()
        raise PDFError(
            f"'{filename}' has {doc.page_count} pages, which exceeds the {MAX_PAGES}-page limit."
        )

    pages = []
    for page_index in range(doc.page_count):
        page = doc[page_index]
        text = page.get_text().strip()  
        if text:  # skip pages with no text (e.g. a blank page, or a scanned image page)
            pages.append((page_index + 1, text))  

    doc.close()

    
    if not pages:
        raise PDFError(
            f"'{filename}' has no extractable text. It may be a scanned document (OCR is not supported yet)."
        )

    return pages
