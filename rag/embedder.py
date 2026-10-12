# Turns chunk text into embedding vectors, in batches

from rag.config import EMBEDDING_MODEL, get_client

BATCH_SIZE = 100  # how many chunks we send per API call


def embed_chunks(chunks: list[dict], api_key: str) -> list[dict]:
    """
    Add an "embedding" field to each chunk dict, computed in batches.

    """
    client = get_client(api_key)

    # Work on a copy 
    chunks = [dict(c) for c in chunks]

    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]
        texts = [c["text"] for c in batch]

        response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)

        
        for chunk, embedding_obj in zip(batch, response.data):
            chunk["embedding"] = embedding_obj.embedding

    return chunks