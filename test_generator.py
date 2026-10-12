# test_generator.py - temporary, tests the full retrieval -> generation flow end-to-end.
import os
from dotenv import load_dotenv

from rag.pdf_reader import extract_pages
from rag.chunker import chunk_pages
from rag.embedder import embed_chunks
from rag.vector_store import VectorStore
from rag.generator import generate_answer
from rag.config import EMBEDDING_MODEL, get_client

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

# Hardcoded question for this test — edit to something specific to your PDF's content.
question = "what is deep learning?"

client = get_client(api_key)
query_embedding = client.embeddings.create(
    model=EMBEDDING_MODEL, input=question
).data[0].embedding

matches = store.query(query_embedding, top_k=3)
answer = generate_answer(question, matches, api_key)

print(f"Question: {question}\n")
print(f"Answer:\n{answer}\n")
print("--- Sources used ---")
for m in matches:
    print(f"- {m['source_filename']}, page {m['page_number']} (distance={m['distance']:.4f})")