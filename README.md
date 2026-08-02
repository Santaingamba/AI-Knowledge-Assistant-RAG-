# AI Knowledge Assistant

A production-grade AI Knowledge Assistant (RAG Application) built with modern software engineering best practices. 

This application allows users to upload PDF documents, processes them using a Retrieval-Augmented Generation (RAG) pipeline with Google Gemini and ChromaDB, and provides a polished chat interface to answer questions strictly based on the uploaded documents.

## Project Overview

- **Frontend**: React 19, TypeScript, Vite, TailwindCSS, shadcn/ui.
- **Backend**: Python 3.12, FastAPI, SQLAlchemy, Pydantic v2.
- **AI/RAG**: LangChain, Gemini API, HuggingFace embeddings (`all-MiniLM-L6-v2`), ChromaDB.
- **Database**: PostgreSQL for relational data (Users, Documents metadata, Chats).
- **Authentication**: JWT with refresh tokens, bcrypt password hashing.
- **Deployment**: Docker and Docker Compose.

## Architecture Diagram

```mermaid
graph TD
    User([User]) -->|HTTPS| React[Frontend (React + Vite)]
    React -->|REST API| FastAPI[Backend (FastAPI)]
    
    FastAPI -->|JWT| Auth[(Auth Service)]
    FastAPI -->|CRUD| Postgres[(PostgreSQL)]
    
    FastAPI -->|PDF Uploads| Storage[Local Storage]
    FastAPI -->|PyMuPDF Text| DocumentService[Document Service]
    
    DocumentService -->|Chunks| Embeddings[sentence-transformers]
    Embeddings -->|Vectors| Chroma[(ChromaDB)]
    
    FastAPI -->|Questions| RAG[RAG Service]
    RAG -->|Similarity Search| Chroma
    Chroma -->|Top K Chunks| RAG
    RAG -->|Prompt + Context| Gemini[Google Gemini API]
    Gemini -->|Answer + Citations| FastAPI
```

## Folder Structure

```
├── backend/
│   ├── app/                # Application code (API, Core, Models, Services)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/                # React code (Components, Pages, Hooks, Services)
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml      # Orchestration
├── .env.example            # Environment variables template
└── README.md
```

## Setup & Installation

### Prerequisites
- Docker and Docker Compose
- Node.js (for local frontend development)
- Python 3.12 (for local backend development)
- A Google Gemini API Key

### Environment Variables
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Update the `.env` file with your `GEMINI_API_KEY` and change the `JWT_SECRET`.

### Docker Setup (Recommended)
You can run the entire stack using Docker Compose:

```bash
docker-compose up --build -d
```
- Frontend will be available at `http://localhost:3000`
- Backend API will be available at `http://localhost:8080`
- Backend API Docs (Swagger) at `http://localhost:8080/docs`

### Local Development Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API Documentation
Once the backend is running, visit `/docs` (e.g., `http://localhost:8080/docs`) to interact with the OpenAPI UI.

## Future Improvements
- Migration from local file storage to AWS S3.
- Advanced RAG techniques (e.g., re-ranking, Hyde).
- WebSockets for chat streaming instead of SSE (Server-Sent Events) or standard polling.
- Role-Based Access Control (RBAC) for team collaboration.
