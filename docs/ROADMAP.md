# AgentHub Learning Roadmap

## Project Philosophy

AgentHub is not built all at once. Every version introduces one new concept, and every version exists because the previous one hit a real limitation. By the end, the project has naturally evolved into an Agentic AI Knowledge Platform — not because that was the plan from day one, but because each limitation forced the next tool.

This roadmap is optimized for learning first, resume second. If you understand *why* each piece exists, the resume framing falls out naturally. If you skip straight to the tools without feeling the problems, you'll have a project you can't defend in an interview.

---

## Project Evolution

```
Foundation
    │
    ▼
AI Chat (talk to Gemini)
    │
    ▼
Reads One Document (no chunking yet)
    │
    ▼
Chunking (handles large documents)
    │
    ▼
Embeddings & Semantic Retrieval (search by meaning)
    │
    ▼
Vector Database (search at scale)
    │
    ▼
Conversation Memory (multi-turn)
    │
    ▼
Agentic Workflow (LangGraph replaces the fixed pipeline)
    │
    ▼
Repository Intelligence (understands code, not just docs)
    │
    ▼
Evaluation (prove it actually works)
```

---

## Development Rules

1. Every version introduces only one new concept.
2. Every version should be completed in a few days, not weeks.
3. Every version must end in a working demo you can run and show.
4. Never implement a feature from a future version, even if it's tempting.
5. Before moving on, you must be able to explain the *problem* the next version solves — in your own words, without notes.
6. After each version, write 3–4 sentences in `docs/DECISIONS.md` explaining what you built and why. If you can't write it without looking at the code, you don't own it yet.

---

# V0 — Foundation

**Goal:** Working dev environment. No AI yet.

**New concept:** None — this is infrastructure.

**Problem this solves:** Nothing yet. This is the ground floor everything else stands on.

**Learning focus:** FastAPI, Docker Compose, environment config, project structure.

**What you'll actually code:**
- FastAPI app with a `/health` endpoint
- `docker-compose.yml` running API + PostgreSQL + Qdrant
- `app/core/config.py` using Pydantic `BaseSettings`
- `.env.example`

**Definition of done:** `docker compose up` starts all three services. `/health` returns HTTP 200.

**Problem you'll hit next:** You have a backend with nothing intelligent in it. Time to actually talk to an LLM.

---

# V1 — AI Chat

**Goal:** Send a question to Gemini, get an answer back.

**New concept:** Calling an LLM API.

**Problem this solves:** You need a baseline before adding any retrieval — you have to feel what a *plain* LLM call can and can't do before you understand why RAG exists.

**Learning focus:** Gemini API, prompt construction, streaming responses.

**What you'll actually code:**
- `POST /chat` endpoint accepting `{"message": "..."}`
- `app/services/llm.py` wrapping the Gemini API call
- Streaming response using FastAPI's `StreamingResponse`
- Basic system prompt

**Definition of done:** You can ask Gemini a general-knowledge question through your API and get a streamed answer.

**Problem you'll hit next:** Ask it something about your own documents — a PDF you have on your desk. It knows nothing. The model only knows what it was trained on.

---

# V2 — AI Reads One Document

**Goal:** Upload a small PDF, ask questions about it.

**New concept:** Document ingestion — getting external text into the model's context.

**Problem this solves:** Direct proof that "stuffing the whole document into the prompt" is the most naive possible way to ground an LLM — and it'll work, for now.

**Learning focus:** PDF text extraction, file uploads.

**What you'll actually code:**
- `POST /documents/upload` accepting a PDF
- Text extraction with `PyMuPDF` or `pdfplumber`
- Pass the *entire* extracted text into the Gemini prompt alongside the user's question
- No storage yet — process and discard, or store raw text only

**Definition of done:** Upload a short PDF (1–3 pages), ask a question about its contents, get a correct grounded answer.

**Problem you'll hit next:** Try a 50-page PDF. It either gets truncated, blows the context window, or makes every request slow and expensive. You can't keep sending the whole document.

---

# V3 — Chunking

**Goal:** Break large documents into manageable pieces.

**New concept:** Chunking.

**Problem this solves:** Large documents exceed context windows and waste tokens sending irrelevant text on every request.

**Learning focus:** Chunk size, overlap, why chunk boundaries matter.

**What you'll actually code:**
- A chunking function: fixed-size chunks (~500 tokens) with overlap (~50 tokens)
- Store chunks with metadata: `doc_id`, `chunk_index`, `source_filename`, raw text
- Store in PostgreSQL for now (a `chunks` table) — no vector DB yet
- Update the chat flow to send *all* chunks from a doc, not the whole raw text

**Definition of done:** Upload a large PDF, confirm it's split into multiple chunks in the database, and the chat endpoint still answers correctly using all chunks.

**Problem you'll hit next:** Sending every chunk on every question still doesn't scale, and it's wasteful — most chunks are irrelevant to any given question. You need to find only the relevant ones.

---

# V4 — Embeddings & Semantic Retrieval

**Goal:** Search chunks by meaning, not exact words.

**New concept:** Embeddings and semantic similarity.

**Problem this solves:** Keyword matching misses synonyms and related concepts — searching "login" won't find a chunk about "authentication." Embeddings represent meaning as vectors, so similar concepts end up close together regardless of exact wording.

**Learning focus:** Embedding models, cosine similarity, what a vector actually represents.

**What you'll actually code:**
- Generate an embedding for each chunk using the Gemini Embedding API, store the vector (a Python list/array is fine — in PostgreSQL as JSON or a simple in-memory cache)
- Embed the incoming question the same way
- Compute cosine similarity manually (numpy is enough) between the question and all chunk embeddings
- Return top-k chunks by similarity score, feed only those into the Gemini prompt
- **Retrieval transparency from here on**: every chat response should show which chunks were used and their similarity scores

**Definition of done:** Ask a question using different wording than the document (e.g. "how do users log in?" against a doc that says "authentication flow") and get the right chunk retrieved.

**Problem you'll hit next:** This works fine with 10 chunks. Try 5 documents and a few thousand chunks — looping through every embedding in Python to compute similarity becomes slow, and you have no easy way to filter by document or persist this across restarts.

---

# V5 — Vector Database

**Goal:** Store and search embeddings at scale.

**New concept:** Vector databases.

**Problem this solves:** Manual cosine similarity in a Python loop doesn't scale past a handful of documents, doesn't persist cleanly, and can't filter by metadata efficiently. A vector database indexes embeddings for fast approximate search and handles persistence and filtering natively.

**Learning focus:** Qdrant, vector indexing, why approximate nearest neighbor search exists.

**What you'll actually code:**
- Qdrant collection setup (vector size matching your embedding model's dimensions)
- Replace the manual similarity loop with Qdrant's search API
- Store chunk metadata (doc_id, filename, chunk text) alongside vectors in Qdrant's payload
- Add filtering (e.g. search within one document only)

**Definition of done:** Same retrieval quality as V4, but backed by Qdrant, with sub-second search even as you add more documents.

**Problem you'll hit next:** Every question is treated independently. Ask a follow-up like "what about the part you mentioned earlier?" and the system has no idea what "earlier" means.

---

# V6 — Conversation History

**Goal:** Multi-turn conversations that remember context.

**New concept:** Conversation state.

**Problem this solves:** Each request so far has been stateless. Real conversations require remembering what was already asked and answered.

**Learning focus:** Chat history storage, prompt construction with history included.

**What you'll actually code:**
- `conversations` and `messages` tables in PostgreSQL
- `POST /chat` returns and accepts a `conversation_id`
- Load the last 3–5 messages and include them in the Gemini prompt alongside retrieved chunks
- No dedicated "memory agent" — history is just a list passed into the prompt

**Definition of done:** Ask a question, then ask a follow-up that only makes sense with prior context. The system answers correctly.

**Problem you'll hit next:** Your code is now a single function doing: load history → embed question → retrieve chunks → maybe skip retrieval if it's a follow-up → build prompt → call LLM. It's becoming a tangle of conditionals that's hard to extend or reason about.

---

# V7 — Agentic Workflow

**Goal:** Replace the fixed pipeline with an explicit, inspectable workflow.

**New concept:** Agent orchestration.

**Problem this solves:** A single function handling retrieval, history, and conditional logic doesn't scale as you add more decision points (which V8 will add). A graph-based workflow makes each step a discrete, testable node and makes the control flow explicit instead of buried in if/else branches.

**Learning focus:** LangGraph, `StateGraph`, state management.

**What you'll actually code:**
- Define `AgentState` (TypedDict): `query`, `messages`, `retrieved_chunks`, `response`
- **Planner node**: decides whether retrieval is needed at all (e.g. "hello" doesn't need a vector search)
- **Retriever node**: runs the Qdrant search from V5, populates `retrieved_chunks`
- **Responder node**: builds the prompt from chunks + history, streams the Gemini response
- Wire with `StateGraph`, compile, replace the V6 pipeline function with a graph invocation

**Definition of done:** Same chat behavior as V6, but now running through a LangGraph graph, and you can trace which node ran for any given request.

**Problem you'll hit next:** The system only knows about uploaded documents. A huge category of real engineering questions — "where is JWT verified?", "explain this function" — needs to search source code, not PDFs.

---

# V8 — Repository Intelligence

**Goal:** Understand GitHub repositories, not just documents.

**New concept:** Code as a retrieval source.

**Problem this solves:** Source code has different structure than prose — file boundaries, function boundaries, language syntax — and is a fundamentally different (and more relevant, given your background) knowledge source than PDFs.

**Learning focus:** Repository parsing, code-aware chunking.

**What you'll actually code:**
- `POST /repositories` accepting a GitHub URL, clone locally (or use GitHub API)
- Parse source files (`.py`, `.js`, `.ts`, `.md` — skip binaries, `node_modules`, etc.)
- Chunk by function/class boundaries where practical, otherwise fall back to fixed-size chunking
- Same embed → store → retrieve pipeline as documents, with `file_path` in metadata instead of `filename`
- Update the Planner node to route code-related questions toward repo chunks

**Definition of done:** Ask "where is JWT verified?" against a cloned repo and get back a relevant code snippet with file path and line context.

**Problem you'll hit next:** You have no way to prove the system actually works well, beyond "I tried a few questions and it seemed right." That's not good enough to claim in an interview.

---

# V9 — Evaluation

**Goal:** Measure whether retrieval and answers are actually correct.

**New concept:** Evaluation.

**Problem this solves:** Without measurement, you're guessing whether the system works. A small evaluation set turns "I think it's good" into "I measured 80% retrieval accuracy on a 10-question test set."

**Learning focus:** Retrieval evaluation, what "good enough" means for RAG.

**What you'll actually code:**
- A hand-written set of 10–15 question/expected-chunk pairs across your test documents and repo
- A script that runs each question through retrieval and checks whether the expected chunk appears in the top-k results
- Report a simple accuracy number
- (Optional, if time allows) Same idea for end-to-end answers: does the generated answer contain the expected fact?

**Definition of done:** You can run one script and get a retrieval accuracy percentage you can quote.

---

## Version 10+ Candidates

Don't build these speculatively — pick based on what the job postings you're actually targeting ask for:

- **Observability (Langfuse)** — if postings mention production monitoring or tracing for LLM systems
- **Tool calling / web search fallback** — if postings emphasize agentic tool use
- **Website crawling** — lower priority, less common in job requirements
- **Team workspaces / multi-user** — only if the role is product-oriented, not infra-oriented

---

## Success Definition

You'll know this roadmap worked if you can confidently explain, without notes:

- Why chunking exists, and what happens without it
- Why embeddings beat keyword search, with a concrete example
- Why a vector database is needed once you have many documents
- Why RAG is more reliable than a plain LLM call, and where it still fails
- Why LangGraph became useful once the pipeline had branching logic
- What your evaluation actually measured, and what its limitations are

The goal isn't to use the most technologies. It's to have hit the real limitation each technology solves, so when an interviewer asks "why did you use X," the answer is a memory, not a definition you memorized.