# Splits page text into token-sized, sentence-aware chunks with overlap.

import re
import tiktoken

CHUNK_SIZE_TOKENS = 700      
OVERLAP_TOKENS = 90          

_encoder = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """How many tokens a string would cost, per the models we use."""
    return len(_encoder.encode(text))


def _split_into_sentences(text: str) -> list[str]:
    """
    Naive sentence splitter: breaks after '.', '!', or '?' followed by whitespace.

    """
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s for s in sentences if s]  # drop any empty strings


def chunk_page(page_number: int, text: str) -> list[tuple[int, str]]:
    """
    Split one page's text into overlapping, sentence-aware chunks.

    """
    sentences = _split_into_sentences(text)
    chunks = []

    current_sentences: list[str] = []   
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)

    
        if current_tokens + sentence_tokens > CHUNK_SIZE_TOKENS and current_sentences:
            chunk_text = " ".join(current_sentences)
            chunks.append((page_number, chunk_text))

            # Build the overlap: keep sentences from the tail of this chunk
            overlap_sentences = []
            overlap_tokens = 0
            for s in reversed(current_sentences):
                t = count_tokens(s)
                if overlap_tokens + t > OVERLAP_TOKENS:
                    break
                overlap_sentences.insert(0, s)
                overlap_tokens += t

            current_sentences = overlap_sentences
            current_tokens = overlap_tokens

        current_sentences.append(sentence)
        current_tokens += sentence_tokens

        # Fallback: a single sentence longer than the whole chunk size (rare, but possible)
        
        if sentence_tokens > CHUNK_SIZE_TOKENS:
            chunk_text = " ".join(current_sentences)
            chunks.append((page_number, chunk_text))
            current_sentences = []
            current_tokens = 0

    if current_sentences:
        chunk_text = " ".join(current_sentences)
        chunks.append((page_number, chunk_text))

    return chunks


def chunk_pages(pages: list[tuple[int, str]]) -> list[dict]:
    """
    Chunk every page of a document and assign a running chunk_id across the whole document.

    """
    all_chunks = []
    chunk_id = 0
    for page_number, text in pages:
        for pg, chunk_text in chunk_page(page_number, text):
            all_chunks.append({
                "chunk_id": chunk_id,
                "page_number": pg,
                "text": chunk_text,
            })
            chunk_id += 1
    return all_chunks
