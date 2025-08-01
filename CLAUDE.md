# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
AI-powered paper reading assistant for Zotero with web interface. Helps users quickly understand and manage research papers through AI-driven analysis and chat interface.

## Architecture
- **Backend**: Python + FastAPI + pyzotero
- **Frontend**: Vue.js
- **Data Source**: Zotero local API
- **AI Integration**: Multi-model API support
- **PDF Processing**: pdf2text for text extraction

## Development Setup

### Backend (FastAPI)
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API docs at http://localhost:8000/docs
```

### Frontend (Vue.js)
```bash
# Install dependencies
cd frontend && pnpm install

# Run development server
pnpm dev

# Build for production
pnpm build
```

## Key Commands
- `uv run pytest` - Run tests
- `uv run black .` - Format Python code
- `uv run ruff check .` - Lint Python code
- `pnpm lint` - Lint frontend code

## Project Structure
```
aizotero/
├── app/                 # FastAPI backend
│   ├── api/            # API routes
│   ├── core/           # Configuration
│   ├── models/         # Pydantic models
│   └── services/       # Business logic
├── frontend/           # Vue.js frontend
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   └── stores/
├── docs/              # Design documents
└── tests/             # Test files
```

## Core Features
1. **List Page**: Display papers from Zotero, show processing status
2. **Reader Page**: PDF viewer on left, AI chat on right
3. **AI Integration**: Paper analysis and Q&A based on content
4. **Zotero Sync**: Local API integration for paper metadata