# test_chunker.py - temporary, tests chunker.py using the same PDF as Step 2.
from rag.pdf_reader import extract_pages
from rag.chunker import chunk_pages, count_tokens

PDF_PATH = "sample.pdf"

with open(PDF_PATH, "rb") as f:
    file_bytes = f.read()

pages = extract_pages(file_bytes, PDF_PATH)
chunks = chunk_pages(pages)

print(f"✅ {len(pages)} pages → {len(chunks)} chunks\n")

for c in chunks:
    tokens = count_tokens(c["text"])
    preview = c["text"][:80].replace("\n", " ")
    print(f"chunk_id={c['chunk_id']:>2}  page={c['page_number']}  tokens={tokens:>3}  \"{preview}...\"")