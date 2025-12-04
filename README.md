# MyAcademicCopilot 🎓🤖  
An AI-powered study assistant for academic courses

MyAcademicCopilot is a full-stack AI assistant that helps students understand course material.
It indexes course PDFs/notes and lets the user ask natural-language questions, using a RAG
(Retrieval-Augmented Generation) pipeline and AI agents.

---

## 🔍 What it can do

- 📂 **Ingest course material** – PDFs and text files (lectures, notes, solved exercises)
- ❓ **Answer questions in natural language** about the uploaded material
- 🧠 **Use RAG** – retrieve the most relevant chunks before calling the LLM
- 🧩 **Agentic behavior** – different “modes” (answer / summarize / explain) via LangGraph
- 📑 **Cited answers** – return both the answer and the supporting document passages
- 📊 **Observability** – log all LLM calls with Langfuse for debugging and evaluation
- 💬 **Chat-style UI** – React/Vite frontend that feels like a modern AI chat app

---

## 🏗️ Architecture & Project Structure

The project is split into two main parts:

```text
MyAcademicCopilot/
  backend/          FastAPI server, RAG & agents
    app/
      agents/       Agent definitions and routing
      LLM/          LLM client abstraction (LiteLLM )
      rag/          RAG pipeline: loader, splitter, retriever, store
      schemas.py    Pydantic request/response models
      main.py       FastAPI app entrypoint
    data/
      *.pdf         Example course materials
      intro_ai.txt  Example text knowledge source
    requirements.txt

  frontend/         React + Vite chat UI
    src/
      components/   Chat UI components (header, sidebar, messages, input, etc.)
      App.jsx       Main app component
      api.js        Client for talking to the backend

## 🔄 High-Level Flow

1. **Document Ingestion**  
   - User provides course materials (PDFs or text files).  
   - Backend loads and parses the documents.  
   - RAG component splits text into chunks and stores embeddings.

2. **User Question**  
   - User sends a natural-language query via the chat interface.  
   - Frontend sends the request to the FastAPI backend.

3. **RAG Retrieval**  
   - Relevant document chunks are retrieved from the vector store.  
   - Retrieved context is attached to the LLM prompt.

4. **AI Agent Execution**  
   - LangGraph selects the appropriate agent (answer, summary, explanation, etc.).  
   - The LLM (via LiteLLM) generates a grounded answer.  

5. **Response Construction**  
   - Backend returns:
     - The answer  
     - The supporting citations (document passages used)  
     - Metadata for debugging/observability (Langfuse trace IDs)

6. **Frontend Display**  
   - The React UI renders the conversation in a chat format.  
   - Citations and context are shown alongside the assistant’s response.


## 🧰 Tech Stack

### Backend
- **Python**, **FastAPI**
- **LangChain**, **LangGraph**
- **LiteLLM 
- **ChromaDB** (in-memory vector store)
- **Pydantic** & **Pydantic-Settings**
- **Langfuse** for observability + tracing
- **Uvicorn** ASGI server

### Frontend
- **React**
- **Vite**

### General
- REST API communication (JSON)
- Modular, clean architecture
- Docker support for easy deployment (full-stack)

