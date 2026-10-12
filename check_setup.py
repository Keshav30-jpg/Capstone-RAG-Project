# check_setup.py - temporary; we'll delete it later.
import os
import sys

from dotenv import load_dotenv

from rag.config import EMBEDDING_MODEL, get_client

load_dotenv()
api_key = os.getenv("LLM_API_KEY")

if not api_key or api_key.startswith("your-"):
    print("❌ No real API key found in .env")
    sys.exit(1)

client = get_client(api_key)
response = client.embeddings.create(model=EMBEDDING_MODEL, input="hello")
print(f"✅ Works via config.py! Embedding length: {len(response.data[0].embedding)}")