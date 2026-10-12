# test_embedder.py - temporary, tests embedder.py on the chunks from Step 3.
import os
from dotenv import load_dotenv

from rag.pdf_reader import extract_pages
from rag.chunker import chunk_pages
from rag.embedder import embed_chunks

load_dotenv()
api_key = os.getenv("LLM_API_KEY")

PDF_PATH = "sample.pdf"

with open(PDF_PATH, "rb") as f:
    file_bytes = f.read()

pages = extract_pages(file_bytes, PDF_PATH)
chunks = chunk_pages(pages)

# To keep this test cheap and fast, only embed the first 2 chunks.
test_chunks = chunks[:2]
embedded = embed_chunks(test_chunks, api_key)

print(f"✅ Embedded {len(embedded)} chunks\n")
for c in embedded:
    vec = c["embedding"]
    print(f"chunk_id={c['chunk_id']}  page={c['page_number']}  "
          f"embedding_length={len(vec)}  first_5_values={vec[:5]}")