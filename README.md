📄 PDF Q&A (RAG)

A Retrieval-Augmented Generation (RAG) web app. Upload one or more PDFs, ask questions in plain language, and get answers grounded only in your documents, with filename and page-number sources.
Built from scratch with the raw OpenAI SDK and the raw ChromaDB SDK: no LangChain or LangGraph.
🔗 Live demo: https://pdfs-based-rag.streamlit.app


Features:

• Multi-PDF support: upload several PDFs in one session and query them together.
• Grounded answers: the model is instructed to answer only from the retrieved PDF text, and to say so when the answer isn't there.
• Citations: every answer comes with an expandable Sources section showing the file and page each piece came from.
• Smart message routing:
     Greetings and small talk get a friendly reply with no retrieval and no quota used.
     A content question with no PDF uploaded shows an inline note and makes no LLM call.
     A content question with a PDF runs the full RAG pipeline.

• Bring your own key: a small key-picker control lets users use the default key (capped) or their own key (no cap, held in memory only).
• Guardrails: 15 MB and 200 pages per PDF, with friendly errors for corrupt or scanned files.
• Session isolation: each visitor gets a private vector collection, so users never see each other's documents.

How it Works:
```text
Upload PDF(s)
   │
   ▼
Extract text per page            (PyMuPDF)
   │
   ▼
Chunk text                       (tiktoken, ~700 tokens, ~13% overlap, sentence-aware)
   │
   ▼
Embed chunks in batches          (text-embedding-3-small)
   │
   ▼
Store in ChromaDB                (metadata: source_filename, page_number, chunk_id)

User asks a question
   │
   ▼
Route the message                (greeting / no PDF / real question)
   │
   ▼
Embed the query → top-5 similarity search
   │
   ▼
Build a context-only prompt → gpt-4o-mini answers with citations
   │
   ▼
Show the answer + expandable Sources
```

Key concepts:

Chunking:
	Pages are split into small, sentence-aware pieces so retrieval returns just the relevant passage instead of a whole page.

Embeddings:
  Each chunk becomes a 1536-number vector that captures its meaning, so searches match on meaning and not just keywords.

Vector similarity:
  The question's vector is compared with the stored chunk vectors, and the closest ones are retrieved.

Grounding:
  The LLM sees only the retrieved chunks and is told not to use outside knowledge.


Tech stack:

```text
Layer                             Choice

UI                                Streamlit
LLM                               openai/gpt-4o-mini via OpenRouter
Embeddings                        openai/text-embedding-3-small via OpenRouter
Vector DB                         ChromaDB (EphemeralClient, in-memory)
PDF parsing                       PyMuPDF(pymupdf)
Tokenizing and chunking           tiktoken with custom chunking logic
SDK                               OpenAI Python SDK pointed at OpenRouter's base URL

```

To Run Locally:
Prerequisites: Python 3.13 (3.12 also works) and an OpenRouter API key.

# 1. Clone the repo
git clone https://github.com/Keshav30-jpg/Capstone-RAG-Project.git
cd Capstone-RAG-Project

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env       # Windows: copy .env.example .env
# then edit .env and set LLM_API_KEY=your-openrouter-key

# 5. Start the app
streamlit run app.py

The app opens at http://localhost:8501


API key and usage limits:
Default key: pre-selected, limited to 10 questions per session, with the window resetting automatically after 4 hours. PDF uploads don't count against the cap.

Your own key: choose "Use my own API key" in the pill near the chat box. There is no cap. The key is stored only in st.session_state (RAM), never written to disk or logs, and cleared when the session ends.

Greetings, no-PDF notes, and failed requests never use up quota.


Limitations:
Scanned or image-only PDFs are not supported (there is no OCR). The app shows a friendly message instead.

The quota lives in the browser session, so refreshing the page resets it. Strictly enforcing it would need server-side storage.

Removing a PDF from the uploader doesn't remove it from the index, and a different file with the same filename is skipped.

Sources lists all retrieved chunks, including weakly related ones. A distance cutoff would trim these.

Greeting detection is rule-based, using a phrase list, so unusual greetings may be treated as questions.

The in-memory index disappears when the app restarts or sleeps.


Interface of webpage:

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/4256b0c4-643d-49a9-9288-026847e22520" />




