# AgentHub Milestones

> Companion file to [ROADMAP.md](./ROADMAP.md). ROADMAP.md explains the *why* behind each version. This file tracks progress and gives the CLI a quick checklist per session.
>
> Rule: do not start a version until the previous one's Definition of Done is fully checked, and you can explain the problem this version solves without looking it up.

---

## Progress

- [ ] V0 — Foundation
- [x] V1 — AI Chat
- [x] V2 — AI Reads One Document

- [x] V3 — Chunking
- [ ] V4 — Embeddings & Semantic Retrieval
- [ ] V5 — Vector Database
- [ ] V6 — Conversation History
- [ ] V7 — Agentic Workflow
- [ ] V8 — Repository Intelligence
- [ ] V9 — Evaluation

---

## V0 — Foundation

**Concept:** None (infrastructure only)

### Deliverables
- [x] FastAPI project scaffold
- [x] `docker-compose.yml` (API + PostgreSQL + Qdrant)
- [x] `app/core/config.py` (Pydantic `BaseSettings`)
- [x] `.env.example`
- [x] `/health` endpoint

### Definition of Done
- [ ] `docker compose up` starts all three services
- [ ] `GET /health` returns HTTP 200

---

## V1 — AI Chat

**Concept:** Calling an LLM

### Deliverables
- [x] `app/services/llm.py` — Gemini API wrapper
- [x] `POST /chat` endpoint
- [x] Streaming response (`StreamingResponse`)
- [x] Basic system prompt

### Definition of Done
- [x] Can ask a general-knowledge question and get a streamed answer
- [x] Can explain: what does the model know, and what does it *not* know?

---

## V2 — AI Reads One Document

**Concept:** Document ingestion

### Deliverables
- [x] `POST /documents/upload` (PDF only for now)
- [x] PDF text extraction (PyMuPDF or pdfplumber)
- [x] Full document text injected into the Gemini prompt

### Definition of Done
- [x] Upload a 1–3 page PDF, ask a question about it, get a correct grounded answer
- [x] Can explain: why does this break on a 50-page PDF?

---

## V3 — Chunking

**Concept:** Chunking

### Deliverables
- [x] Chunking function (~500 tokens, ~50 token overlap)
- [x] `chunks` table in PostgreSQL (doc_id, chunk_index, source_filename, text)
- [x] Chat flow updated to use all chunks for a document

### Definition of Done
- [x] Upload a large PDF, confirm multiple chunks stored
- [x] Chat endpoint still answers correctly using all chunks
- [x] Can explain: why is sending every chunk on every question wasteful?

---

## V4 — Embeddings & Semantic Retrieval

**Concept:** Embeddings, semantic similarity

### Deliverables
- [ ] Generate embeddings per chunk (Gemini Embedding API)
- [ ] Embed incoming questions
- [ ] Manual cosine similarity (numpy) — no vector DB yet
- [ ] Top-k chunk retrieval
- [ ] **Retrieval transparency**: show chunks used + similarity scores in every response (keep this from here on)

### Definition of Done
- [ ] A question phrased differently from the document text still retrieves the right chunk
- [ ] Can explain: why does keyword search fail here, and why does cosine similarity fix it?

---

## V5 — Vector Database

**Concept:** Vector databases

### Deliverables
- [ ] Qdrant collection created (correct vector size for embedding model)
- [ ] Replace manual similarity loop with Qdrant search
- [ ] Chunk metadata stored in Qdrant payload
- [ ] Filtering by document_id

### Definition of Done
- [ ] Same retrieval quality as V4, now via Qdrant
- [ ] Can explain: at what scale does manual cosine similarity stop working, and why?

---

## V6 — Conversation History

**Concept:** Conversation state

### Deliverables
- [ ] `conversations` and `messages` tables
- [ ] `POST /chat` accepts/returns `conversation_id`
- [ ] Last 3–5 messages included in prompt

### Definition of Done
- [ ] A follow-up question that depends on prior context is answered correctly
- [ ] Can explain: why is this not a separate "Memory Agent"?

---

## V7 — Agentic Workflow

**Concept:** Agent orchestration

### Deliverables
- [ ] `AgentState` TypedDict (query, messages, retrieved_chunks, response)
- [ ] Planner node (decides if retrieval is needed)
- [ ] Retriever node (Qdrant search)
- [ ] Responder node (prompt + streaming response)
- [ ] `StateGraph` wired and replacing the V6 pipeline function

### Definition of Done
- [ ] Same behavior as V6, now running through LangGraph
- [ ] Can trace which node ran for a given request
- [ ] Can explain: what problem does LangGraph solve that the V6 pipeline function didn't?

---

## V8 — Repository Intelligence

**Concept:** Code as a retrieval source

### Deliverables
- [ ] `POST /repositories` (GitHub URL → clone)
- [ ] Source file parsing (skip binaries, node_modules, etc.)
- [ ] Code-aware chunking (function/class boundaries where practical)
- [ ] Repo chunks embedded and stored in Qdrant (file_path metadata)
- [ ] Planner node updated to route code questions to repo chunks

### Definition of Done
- [ ] "Where is JWT verified?" against a real repo returns a relevant snippet with file path
- [ ] Can explain: how is chunking code different from chunking prose?

---

## V9 — Evaluation

**Concept:** Evaluation

### Deliverables
- [ ] 10–15 hand-written question/expected-chunk pairs
- [ ] Script that checks if expected chunk appears in top-k retrieval results
- [ ] Reported accuracy number
- [ ] (Optional) End-to-end answer correctness check

### Definition of Done
- [ ] One script run produces a retrieval accuracy percentage
- [ ] Can explain: what does this number actually tell you, and what doesn't it tell you?

---

## Version 10+ (pick based on target job postings, do not build speculatively)

- [ ] Observability (Langfuse)
- [ ] Tool calling / web search fallback
- [ ] Website crawling
- [ ] Team workspaces / multi-user

---

## Per-Version Checklist (apply every time)

1. [x] Read the version's section in [ROADMAP.md](./ROADMAP.md) before starting
2. [x] CLI proposes architecture before writing code — review and question it
3. [x] Implement, review every generated line
4. [x] Run it, break it, fix it
5. [x] Write 3–4 sentences in `docs/DECISIONS.md`, in your own words
6. [x] Check off Definition of Done items
7. [x] Commit with a `feat:` / `fix:` / `docs:` message
8. [ ] Update resume bullet if this version adds a new demonstrable skill