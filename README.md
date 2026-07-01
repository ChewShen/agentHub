# AgentHub

An Agentic AI Knowledge Platform built incrementally — each version introduces one new concept and exists because the previous version hit a real limitation.

## What Is This?

AgentHub is a RAG (Retrieval-Augmented Generation) system that lets you ask natural language questions about your documents and code repositories. It combines an LLM with semantic search over your own data, so answers are grounded in your actual content — not just what the model was trained on.

The project is built version by version, following a learning-first approach:

| Version | Concept | What It Adds |
|---------|---------|--------------|
| **V0** | Foundation | FastAPI scaffold, Docker Compose, core config |
| V1 | LLM Calls | Chat with Gemini via API |
| V2 | Document Ingestion | Upload a PDF, ask questions about it |
| V3 | Chunking | Break large documents into searchable pieces |
| V4 | Embeddings | Search by meaning, not keywords |
| V5 | Vector Database | Scale search with Qdrant |
| V6 | Conversation Memory | Multi-turn chat with context |
| V7 | Agentic Workflow | LangGraph orchestration |
| V8 | Repository Intelligence | Understand code, not just documents |
| V9 | Evaluation | Prove retrieval quality with metrics |

> **Current version: V0 — Foundation**

## Tech Stack

- **Backend:** Python 3.12, FastAPI, Pydantic
- **Database:** PostgreSQL 16
- **Vector Store:** Qdrant
- **Containerization:** Docker Compose
- **LLM:** Google Gemini *(from V1)*

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### Run

```bash
# Clone the repo
git clone https://github.com/your-username/agentHub.git
cd agentHub

# Create your environment file
cp .env.example .env

# Build and start all services
docker compose up --build

# Verify it works (in another terminal)
curl http://localhost:8000/health
# → {"status": "healthy"}
```

### Run Tests

```bash
# Create a virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

## Project Structure

```
agentHub/
├── app/
│   ├── main.py              # FastAPI application + /health endpoint
│   └── core/
│       └── config.py         # Pydantic BaseSettings (env config)
├── tests/
│   └── test_health.py        # Integration tests
├── docs/
│   ├── ROADMAP.md            # Why each version exists
│   ├── milestones.md         # Progress checklist per version
│   └── decision.md           # Architecture decision log
├── docker-compose.yml        # API + PostgreSQL + Qdrant
├── Dockerfile
├── requirements.txt
├── .env.example
└── agents.md                 # Development rules and conventions
```

## Philosophy

Every version introduces exactly one new concept. No feature is added until the previous version's limitation is felt firsthand. The goal is understanding — not a feature checklist.

See [docs/ROADMAP.md](docs/ROADMAP.md) for the full reasoning behind each version.

## License

This is a personal learning and portfolio project.
