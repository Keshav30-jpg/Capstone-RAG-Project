from rag.config import CHAT_MODEL, get_client

SYSTEM_PROMPT = """You are a helpful assistant that answers questions using ONLY the \
provided context from uploaded PDF documents.

Rules:
- Answer only using information found in the context below. Do not use outside knowledge.
- If the answer is not in the context, say so clearly instead of guessing.
- After each claim, cite the source like this: [filename, page X].
- If multiple sources support a claim, cite all of them.
- Keep answers concise and directly responsive to the question."""


def _build_context(matches: list[dict]) -> str:
    """
    Each chunk is labeled with its filename and page, right next to the text,
    
    """
    blocks = []
    for i, m in enumerate(matches, start=1):
        blocks.append(
            f"[Source {i}: {m['source_filename']}, page {m['page_number']}]\n{m['text']}"
        )
    return "\n\n".join(blocks)


def generate_answer(question: str, matches: list[dict], api_key: str) -> str:
    """
    Ask gpt-4o-mini to answer a question using only the retrieved chunks.

    """
    context = _build_context(matches)

    user_message = f"""Context:
{context}

Question: {question}"""

    client = get_client(api_key)
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,  
    )

    return response.choices[0].message.content
