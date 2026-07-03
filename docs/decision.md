## V0 — Foundation
1. What is built
- For this v0, is just scaffolding, foundation setup and the dcoker for containerize setup. No feature is built yet.
- By doing `curl http://localhost:8000/health`, the status of the server can be check on

2. Why all the services?
- The services like postgreSQL and Qdrant are planned to be add on in future, its added now is to laid the foundation so it wont messed up during the future implementation. Since it was planned, why not just add it if can.

3. Trade-Off
- There are no fancy folder yet is to minimise and reduce the complexity of the project. Too many unused folder will often lead to messy implementation and the losing track of the actual progress/milestone.

## V1 — AI Chat
1. What is built
- A stateless `POST /chat` endpoint that sends a message to the Gemini API (`gemini-3.1-flash-lite`) and streams the text response back.

2. Why Gemini and why this version?
- Gemini was chosen over other free tiers because it natively supports multimodality (crucial for V2 when we ingest PDFs/images), has a massive context window for testing "naive RAG", and the `google-genai` SDK plays nicely with async FastAPI.
- This version establishes a baseline. It proves we can talk to an LLM, but quickly highlights the limitation: the model only knows its training data. If we ask it about our private documents, it will fail, setting up the exact problem V2 solves.

3. Trade-Offs & Tech Debt
- We instantiated the Gemini client as a global singleton during the FastAPI lifespan. It's pragmatic for now, but in a larger app, proper dependency injection would be better.
- There is no conversation history (every request is a blank slate) and no retry logic for API failures.