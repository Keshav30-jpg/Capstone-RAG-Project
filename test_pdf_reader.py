# test_pdf_reader.py - temporary, just to test pdf_reader.py in isolation.
from rag.pdf_reader import extract_pages, PDFError

# Change this to the path of any real PDF you have on your machine.
PDF_PATH = "sample.pdf"

with open(PDF_PATH, "rb") as f:
    file_bytes = f.read()

try:
    pages = extract_pages(file_bytes, PDF_PATH)
    print(f"✅ Extracted {len(pages)} pages with text.\n")
    # Print just the first page's first 300 characters, as a sanity check.
    first_page_num, first_page_text = pages[0]
    print(f"--- Page {first_page_num} preview ---")
    print(first_page_text[:300])
except PDFError as e:
    print(f"❌ {e}")