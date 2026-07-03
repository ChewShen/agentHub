# Architecture Decisions

This file tracks the key technical decisions made during the AgentHub roadmap. 
Each version must add a short entry explaining the problem solved and the approach chosen.

## V1 — AI Chat
**Decision:** We implemented a streaming `POST /chat` endpoint using the `google-genai` SDK and FastAPI's `StreamingResponse`.
**Why:** To establish a baseline LLM connection before introducing any retrieval. We kept the service layer clean (handling client lifecycle and exceptions) so the router only worries about HTTP.

## V2 — AI Reads One Document
**Decision:** We created a single `POST /documents/upload` endpoint that takes a PDF and a question, extracts the text using `PyMuPDF`, and injects the entire text into the Gemini system prompt.
**Why:** This is the most naïve form of RAG. It proves that passing external knowledge to the model works, but intentionally exposes the context-window limitation by doing no chunking or storage. We chose `PyMuPDF` for its speed and C-based efficiency compared to pure Python alternatives. We chose a single-request flow (process and discard) to keep the scope tight and avoid premature database design.
