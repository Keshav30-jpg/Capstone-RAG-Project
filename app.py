# app.py  the full Streamlit chat UI

import streamlit as st

from rag.pdf_reader import extract_pages, PDFError
from rag.chunker import chunk_pages
from rag.embedder import embed_chunks
from rag.vector_store import VectorStore
from rag.generator import generate_answer
from rag.router import route_message, RouteType
from rag.config import EMBEDDING_MODEL, get_client
from rag import key_manager as km

st.set_page_config(
    page_title="PDF Q&A",
    page_icon="🗒️",
    layout="centered",
)

# Session state setup
km.init_key_state()

if "vector_store" not in st.session_state:
    st.session_state.vector_store = VectorStore()  # one shared collection per session

if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = set()  # filenames already embedded, to avoid re-indexing

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of {"role": "user"/"assistant", "content": str, "sources": list|None}

def render_sources(sources: list[dict]) -> None:
    """Show each cited document page once, even if several chunks came from it."""
    seen = set()
    for source in sources:
        source_key = (source["source_filename"], source["page_number"])
        if source_key in seen:
            continue
        seen.add(source_key)
        st.caption(f"📄 {source_key[0]}, page {source_key[1]}")


def render_user_message(content: str) -> None:
    """Place a user message on the right while keeping assistant replies left."""
    _, message_column = st.columns((1, 1), gap="small")
    with message_column:
        with st.chat_message("user", avatar=":material/person:"):
            st.write(content)


with st.sidebar:
    st.title("PDF Q&A")
    st.badge("Document assistant", color="violet")
    st.caption("Ask with confidence. Verify with sources.")

    with st.expander("Session settings", icon=":material/tune:", expanded=True):
        km.render_key_selector()
        st.caption("Choose which API key powers this session.")

    with st.expander(
        "How this RAG workflow works",
        icon=":material/account_tree:",
    ):
        st.caption("Your PDFs are processed only for this browser session.")

        st.markdown("**1. Upload and validate**")
        st.caption(
            "PDF files are accepted up to 15 MB and 200 pages. "
            "PyMuPDF reads the text page by page; scanned PDFs without selectable text are not supported."
        )

        st.markdown("**2. Split into useful chunks**")
        st.caption(
            "Text is split by sentence using the cl100k_base tokenizer: "
            "700-token chunks with a 90-token overlap to preserve nearby context."
        )

        st.markdown("**3. Create embeddings**")
        st.caption(
            "Chunks are embedded in batches of 100 with OpenRouter using "
            "openai/text-embedding-3-small."
        )

        st.markdown("**4. Store and retrieve**")
        st.caption(
            "ChromaDB stores embeddings in an in-memory vector collection for this session. "
            "When you ask a question, the same embedding model finds the 5 closest chunks."
        )

        st.markdown("**5. Generate a source-backed answer**")
        st.caption(
            "GPT-4o-mini receives only the retrieved text, answers from that context, "
            "and cites the PDF filename and page number for each claim."
        )

        st.markdown("**6. Keep the session controlled**")
        st.caption(
            "Greetings and questions without a PDF are handled before retrieval. "
            "The default key allows 10 RAG questions per 4-hour window; your own key is kept in memory only."
        )
    st.caption("Your uploads and chat history are available only for this browser session.")


if not st.session_state.chat_history:
    st.space("large")
    st.title("Welcome to PDF Q&A", icon="🗒️", text_alignment="center")
    st.caption(
        "Ask clear questions about your PDFs and verify every answer with its page sources.",
        text_alignment="center",
    )
    st.space("small")

else:
    with st.container(horizontal=True, vertical_alignment="center", gap="small"):
        st.subheader("PDF Q&A")
        st.badge("Source-backed", icon=":material/verified:", color="blue")


# Render chat history before the input so completed answers remain above it.
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        render_user_message(msg["content"])
    else:
        with st.chat_message("assistant", avatar=":material/smart_toy:"):
            st.write(msg["content"])
            if msg.get("sources"):
                with st.expander("Sources", icon=":material/format_quote:"):
                    render_sources(msg["sources"])


# Chat input + routing + pipeline.
user_input = st.chat_input("Ask a question about your PDFs...", key="pdf_question")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input, "sources": None})
    render_user_message(user_input)

    has_pdf = len(st.session_state.indexed_files) > 0
    route = route_message(user_input, has_pdf)

    with st.chat_message("assistant", avatar=":material/smart_toy:"):
        if route == RouteType.GREETING:
            answer = (
                "Hello! What would you like to know about your uploaded PDFs?"
                if has_pdf
                else "Hello! Upload a PDF and ask me anything about it."
            )
            st.write(answer)
            st.session_state.chat_history.append({"role": "assistant", "content": answer, "sources": None})

        elif route == RouteType.NO_PDF:
            answer = "Please upload a relevant PDF to ask this question."
            st.info(answer)
            st.session_state.chat_history.append({"role": "assistant", "content": answer, "sources": None})

        else:
            if not km.can_ask_question():
                answer = (
                    "You've reached the default key's question limit for this session. "
                    "Switch to your own API key above to continue, or wait for the 4-hour window to reset."
                )
                st.warning(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer, "sources": None})
            else:
                with st.spinner("Searching your PDFs..."):
                    api_key = km.get_active_api_key()
                    client = get_client(api_key)
                    query_embedding = client.embeddings.create(
                        model=EMBEDDING_MODEL, input=user_input
                    ).data[0].embedding

                    matches = st.session_state.vector_store.query(query_embedding, top_k=5)
                    answer = generate_answer(user_input, matches, api_key)

                km.record_question_asked()  # Only counts against quota on a real RAG call.

                st.write(answer)
                with st.expander("Sources", icon=":material/format_quote:"):
                    render_sources(matches)

                st.session_state.chat_history.append({
                    "role": "assistant", "content": answer, "sources": matches,
                })
    st.rerun()


with st.expander(
    "Add PDFs to this chat",
    icon=":material/upload_file:",
    expanded=not st.session_state.indexed_files,
):
    st.caption("PDF only · Up to 15 MB and 200 pages per file")
    uploaded_files = st.file_uploader(
        "Upload PDFs", type="pdf", accept_multiple_files=True
    )

    if uploaded_files:
        for f in uploaded_files:
            filename = f.name
            if filename in st.session_state.indexed_files:
                continue

            with st.spinner(f"Indexing {filename}..."):
                try:
                    pages = extract_pages(f.getvalue(), filename)
                    chunks = chunk_pages(pages)
                    embedded = embed_chunks(chunks, km.get_active_api_key())
                    st.session_state.vector_store.add_chunks(embedded, source_filename=filename)
                    st.session_state.indexed_files.add(filename)
                    st.success(f"Indexed {filename} ({len(chunks)} chunks)", icon=":material/check_circle:")
                except PDFError as e:
                    st.error(str(e), icon=":material/error:")

    if st.session_state.indexed_files:
        document_count = len(st.session_state.indexed_files)
        st.badge(
            f"{document_count} document{'s' if document_count != 1 else ''} ready",
            icon=":material/check_circle:",
            color="blue",
        )
        for filename in sorted(st.session_state.indexed_files):
            st.caption(f":material/description: {filename}")
