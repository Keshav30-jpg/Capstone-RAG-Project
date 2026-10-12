# test_vector_store.py - temporary, tests vector_store.py end-to-end on real chunks.
import os
from dotenv import load_dotenv

from rag.pdf_reader import extract_pages
from rag.chunker import chunk_pages
from rag.embedder import embed_chunks
from rag.vector_store import VectorStore

load_dotenv()
api_key = os.getenv("LLM_API_KEY")

PDF_PATH = "sample.pdf"

with open(PDF_PATH, "rb") as f:
    file_bytes = f.read()

pages = extract_pages(file_bytes, PDF_PATH)
chunks = chunk_pages(pages)
embedded_chunks = embed_chunks(chunks, api_key)

store = VectorStore()
store.add_chunks(embedded_chunks, source_filename=PDF_PATH)
print(f"✅ Stored {store.count()} chunks in the collection\n")

# Now simulate a real query: embed a question and search for relevant chunks.
from rag.config import EMBEDDING_MODEL, get_client

client = get_client(api_key)

question = "What is this document about?"  # edit this to something relevant to your PDF
query_embedding = client.embeddings.create(
    model=EMBEDDING_MODEL, input=question
).data[0].embedding

results = store.query(query_embedding, top_k=3)

print(f"Query: \"{question}\"\n")
for r in results:
    preview = r["text"][:100].replace("\n", " ")
    print(f"distance={r['distance']:.4f}  page={r['page_number']}  "
          f"file={r['source_filename']}\n  \"{preview}...\"\n")