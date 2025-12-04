Academic Knowledge Copilot 🎓

An AI-powered study assistant that helps students understand course material.

The system:
- Indexes course documents (lectures, notes, solved exercises) using RAG.
- Lets students ask free-text questions about the material.
- Uses mode-specific AI agents (answer, summary, email, etc.) to respond.
- Returns both the answer and document citations used as context.
- Tracks all LLM calls with Langfuse for observability and debugging.

Tech stack:
- Backend: FastAPI, Python, LiteLLM, Gemini 2.5 Flash
- RAG: custom in-memory vector store with embeddings
- Observability: Langfuse
- Frontend: React (chat-style UI)
