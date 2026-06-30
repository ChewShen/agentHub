# AGENTS.md

## Project Overview

AgentHub is an Agentic AI Knowledge Platform built to demonstrate production-oriented AI Engineering skills: Retrieval-Augmented Generation (RAG), LangGraph workflows, vector databases, FastAPI backend development, Docker deployment, and evaluation.

This is a learning project first, a portfolio project second. Every version exists because the previous version hit a real limitation — see [docs/ROADMAP.md](./docs/ROADMAP.md) for the full reasoning and [docs/milestones.md](./docs/milestones.md) for the current checklist. Do not skip ahead to a tool or technique before the version that introduces it.

The goal is a maintainable, production-inspired system — not a prototype or hackathon project, and not a feature checklist implemented without understanding.

---

## Engineering Principles

- Clean architecture over quick hacks.
- Readability over clever code.
- Single responsibility per function.
- No premature optimization.
- Follow FastAPI best practices.
- Type hints everywhere — no exceptions.
- Business logic lives in services, not routes.
- Async-first. Use sync only when a library forces it.

---

## Development Rules

- Do not introduce new dependencies without justification.
- Do not generate unused code.
- Never create placeholder implementations without a `# TODO:` comment explaining what's missing and why.
- Explain architectural decisions before implementing major features.
- When requirements are ambiguous, ask — do not assume.
- Do not implement anything from a future version in [docs/milestones.md](./docs/milestones.md), even if it seems like a natural extension. Ask first if something feels like it belongs in a later version.
- All new business logic must have at least one unit test.
- Handle errors explicitly. Never let exceptions propagate silently.

---

## Code Style

### Backend

- FastAPI for all API routes
- SQLAlchemy ORM (async where supported) — introduced from V2 onward when persistence is needed
- Pydantic models for request/response validation and config
- `app/services/` for business logic — routes only call services
- `app/core/config.py` using Pydantic `BaseSettings` for all environment config
- Consistent error responses via `HTTPException` with structured detail fields

### Error Response Format

All errors must follow this shape:

```json
{
  "detail": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}
```

### Frontend

- Minimal UI. Backend functionality has priority.
- No UI work until the relevant backend endpoint is complete and tested.

---

## Configuration & Secrets

- All config loaded from environment variables via `app/core/config.py`
- Never hardcode secrets, URLs, or credentials
- `.env.example` must be kept up to date whenever new variables are added
- `.env` is always in `.gitignore`

---

## Authentication — Explicitly Out of Scope For Now

JWT auth, user accounts, and role-based access are **not** part of V0–V9. The roadmap is single-user and local-first by design, so effort goes into RAG and agent concepts instead of auth boilerplate.

Auth may be revisited as a "Version 10+" candidate, only if it's relevant to the specific jobs being targeted at that time. Do not add login, registration, or protected routes unless explicitly instructed.

---

## Testing

- Unit tests for all service-layer functions
- Integration tests for API endpoints (use `httpx.AsyncClient` with FastAPI's test client)
- Tests live in `tests/` mirroring the `app/` structure
- Run tests before committing: `pytest`
- From V9 onward, retrieval/answer quality is also checked via the evaluation script — not just unit tests

---

## Git Workflow

Each version must produce a working, runnable application.

Commit format:
```
feat: short description
fix: short description
refactor: short description
docs: short description
test: short description
```

- One concern per commit.
- Never mix features, fixes, and tests in a single commit.

---

## Current Version

See [docs/milestones.md](./docs/milestones.md) for the live checklist and Definition of Done per version. Update that file's "Progress" section, not this one, as versions are completed.

Do not start the next version until:
1. The current version's Definition of Done is fully checked, and
2. You can explain the problem the *next* version solves, in your own words, without notes.

---

## When Implementing Features

### Before writing code:

1. Explain the proposed architecture.
2. List files to be created or modified.
3. State trade-offs and alternatives considered.
4. Get confirmation if the scope is large.

### After implementation:

1. Explain how to test the feature manually.
2. Confirm tests are written.
3. Identify known limitations or future improvements.
4. Suggest a Git commit message.

### After each version is complete:

1. Remind me to write a short entry in `docs/DECISIONS.md` summarizing the choice and trade-offs, in my own words.
2. Ask: "What would a senior backend engineer criticize about this implementation?"
3. Ask: "What technical debt did we introduce?"
4. Confirm the relevant checklist items in `docs/milestones.md` are ready to be checked off.