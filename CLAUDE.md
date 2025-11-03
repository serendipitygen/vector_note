# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Vector Note is a full-stack note-taking application with AI-powered chat and vector search capabilities. The application consists of:
- **Backend**: FastAPI (Python) with PostgreSQL database and vector search using Qdrant/Milvus
- **Frontend**: React with TypeScript and Material-UI
- **AI Integration**: Google Gemini API for chat functionality and embeddings

## Architecture

### Backend Structure (FastAPI)
```
backend/app/
├── api/endpoints/          # API route handlers
│   ├── auth.py            # Authentication endpoints
│   ├── notes.py           # Note CRUD operations
│   └── chat.py            # AI chat functionality
├── core/                  # Core configuration
│   ├── config.py          # Settings using pydantic-settings
│   ├── security.py        # JWT and password hashing
│   └── deps.py            # Dependency injection
├── db/                    # Database setup
│   ├── session.py         # SQLAlchemy session
│   └── base.py            # Database base and initialization
├── models/                # SQLAlchemy ORM models
│   ├── note.py
│   ├── chat.py
│   └── clipboard.py
├── schemas/               # Pydantic schemas for validation
├── services/              # Business logic
│   ├── gemini_service.py      # Google Gemini API integration
│   ├── embedding_service.py   # Text embeddings
│   ├── chat_service.py        # Chat functionality
│   ├── milvus_service.py      # Vector database operations
│   └── content_extractor.py   # Document parsing (PDF, DOCX)
└── main.py                # FastAPI app initialization and CORS
```

### Frontend Structure (React + TypeScript)
```
frontend/src/
├── components/
│   ├── Auth.tsx           # Login/Registration
│   ├── NoteList.tsx       # Note display and management
│   ├── AddNote.tsx        # Note creation
│   ├── Chat.tsx           # AI chat interface
│   └── Layout.tsx         # Main layout wrapper
├── contexts/
│   └── AuthContext.tsx    # Authentication state management
├── config.ts              # API endpoint configuration
└── App.tsx                # Main app component with routing
```

### Key Integration Points
- **Authentication**: JWT-based auth flow between frontend AuthContext and backend auth endpoints
- **API Communication**: Frontend uses axios to communicate with backend at `http://localhost:8000/api/v1`
- **Vector Search**: Notes are embedded using sentence transformers and stored in Qdrant/Milvus for semantic search
- **AI Chat**: Uses Google Gemini API through backend service layer for chat responses

## Development Commands

### Database Setup (PostgreSQL)
```bash
# Connect to PostgreSQL and create database
psql -U postgres

# Run these SQL commands:
CREATE USER vector_note WITH PASSWORD 'vector_note_password';
CREATE DATABASE vector_note;
GRANT ALL PRIVILEGES ON DATABASE vector_note TO vector_note;
```

### Backend Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
cd backend
alembic upgrade head

# Start backend server (from project root)
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API documentation available at:
# http://localhost:8000/api/v1/docs (Swagger)
# http://localhost:8000/api/v1/redoc (ReDoc)
```

### Frontend Development
```bash
# Install dependencies
cd frontend
npm install

# Start development server (runs on port 4996)
npm start

# Run tests
npm test

# Build for production
npm run build
```

### Process Management
```bash
# Kill all running processes (Windows)
taskkill /F /IM node.exe & taskkill /F /IM python.exe

# Kill only Node processes
taskkill /F /IM node.exe
```

## Environment Configuration

### Backend (.env in project root)
Required environment variables:
- `GOOGLE_API_KEY`: Google Gemini API key for chat and embeddings
- `POSTGRES_SERVER`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: Database configuration
- `SECRET_KEY`: JWT secret key for authentication
- `QDRANT_URL`, `QDRANT_API_KEY`: Vector database configuration (optional)

See `.env.example` for full list of available configuration options.

### Frontend
Frontend port is configured in `package.json` scripts to use port 4996.
API endpoint is configured in `frontend/src/config.ts`.

## Important Notes

### Security
- API keys must never be committed to git. Use `.env` files (already in `.gitignore`)
- The `.cursor` directory is in `.gitignore` to prevent exposure of configuration
- JWT tokens are used for authentication with configurable expiration

### Database
- The application uses PostgreSQL with SQLAlchemy ORM
- Alembic is configured for database migrations
- A SQLite database file (`vector_note.db`) exists in the backend directory but appears to be legacy

### Vector Search
- The application supports both Qdrant and Milvus for vector storage
- Embeddings are generated using sentence-transformers models
- Vector search enables semantic similarity search across notes

### Dependencies
Key Python packages:
- `fastapi`, `uvicorn`: Web framework and server
- `sqlalchemy`, `alembic`: Database ORM and migrations
- `langchain`, `langchain-google-genai`: AI integration framework
- `sentence-transformers`: Text embeddings
- `qdrant-client`, `pymilvus`: Vector databases
- `python-jose`, `passlib`: Authentication and security

Key NPM packages:
- `react`, `react-dom`, `react-router-dom`: React framework and routing
- `@mui/material`, `@emotion/react`: Material-UI components
- `axios`: HTTP client for API calls
- `typescript`: Type safety
