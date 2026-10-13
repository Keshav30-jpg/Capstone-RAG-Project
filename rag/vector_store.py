import uuid
import chromadb
import streamlit as st

@st.cache_resource
def _get_client():
    """
    st.cache_resource keeps it alive across reruns and sessions, so it is never
     down while another session is trying to use it

    """
    return chromadb.EphemeralClient()

class VectorStore:
    """
    One VectorStore = one private collection for one user session.

    """
    def __init__(self):
        self._client = _get_client()
        # A random unique name gives each session its own collection, so users
        self._collection = self._client.create_collection(name=f"session_{uuid.uuid4().hex}")

        
            

    def add_chunks(self, chunks: list[dict], source_filename: str) -> None:
        """
        Store embedded chunks from one PDF into the collection.

        """
        # Chroma needs a unique string "id" per entry across the WHOLE collection.
        ids = [f"{source_filename}::{c['chunk_id']}" for c in chunks]
        embeddings = [c["embedding"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [
            {
                "source_filename": source_filename,
                "page_number": c["page_number"],
                "chunk_id": c["chunk_id"],
            }
            for c in chunks
        ]

        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        """
        Find the top_k chunks most similar to a query embedding.

        """
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        # query we sent — we only sent one, so we index [0] to unwrap it).
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        matches = []
        for doc, meta, dist in zip(documents, metadatas, distances):
            matches.append({
                "text": doc,
                "source_filename": meta["source_filename"],
                "page_number": meta["page_number"],
                "chunk_id": meta["chunk_id"],
                "distance": dist,
            })
        return matches

    def count(self) -> int:
        """How many chunks are currently stored."""
        return self._collection.count()