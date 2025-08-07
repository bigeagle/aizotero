# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered paper reading assistant for Zotero with web interface. Helps users quickly understand and manage research papers through AI-driven analysis and chat interface.

## Architecture

- **Backend**: Python + FastAPI + aiohttp (async)
- **Frontend**: Vue.js + TypeScript + Tailwind CSS v4
- **Data Source**: Zotero local API (async via aiohttp)
- **AI Integration**: OpenAI compatible API support
- **PDF Processing**: markitdown with ThreadPoolExecutor (async)
- **Styling**: Tailwind CSS v4 with @tailwindcss/typography plugin
- **Storage**: SQLite for chat history, file-based caching for PDF processing

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

### Backend
- `uv run -m pytest` - Run all tests
- `uv run -m pytest app/tests/test_main.py::test_specific_function` - Run single test
- `uv run black .` - Format Python code
- `uv run ruff check .` - Lint Python code
- `uv run ruff check . --fix` - Auto-fix linting issues
- `uv run lefthook run pre-commit` - Run all git hooks

### Frontend
- `pnpm dev` - Start frontend dev server
- `pnpm build` - Build frontend for production
- `pnpm lint` - Lint frontend code
- `pnpm type-check` - TypeScript type checking
- `pnpm format` - Format frontend code with Prettier
- `pnpm preview` - Preview production build locally

## Core Architecture Patterns

### Async Design Patterns
- **ThreadPoolExecutor for sync operations**: PDF processing uses ThreadPoolExecutor to avoid blocking async event loop
- **aiohttp for all external HTTP calls**: All Zotero API calls use aiohttp with proper session management
- **Database operations**: SQLite operations use aiosqlite for async support

### Service Layer Architecture
- **ZoteroService** (`app/services/zotero_service.py`): Handles all Zotero API interactions with async session management
- **PDFParserService** (`app/services/pdf_parser.py`): Async PDF processing with file-based caching using MD5 hashes
- **ChatDatabase** (`app/services/database.py`): SQLite-based chat history persistence with JSON storage

### Caching Strategy
- **PDF content caching**: MD5-based file content caching in `data/cache/markitdown/`
- **ArXiv metadata caching**: Paper metadata cached in `data/cache/arxiv/metadata/`
- **PDF files caching**: Downloaded PDFs cached in `data/cache/arxiv/pdf/`

### Frontend State Management
- **Pinia stores**: Centralized state management with `aiStore.ts` for AI configuration
- **Service layer**: API calls abstracted in `services/` directory
- **Component composition**: Reusable components with clear separation of concerns

## Key Files & Directories

### Backend Services
- `app/services/zotero_service.py`: Async Zotero API client (user_id=0 for local API)
- `app/services/pdf_parser.py`: Async PDF to markdown conversion with caching
- `app/services/database.py`: SQLite chat history persistence
- `app/services/arxiv_service.py`: ArXiv paper fetching with caching

### API Endpoints
- `/api/v1/papers` - Zotero paper management
- `/api/v1/arxiv` - ArXiv integration endpoints
- `/api/v1/chat` - AI chat and paper analysis

### Frontend Components
- `frontend/src/components/AIChat.vue`: Main chat interface with markdown/KaTeX support
- `frontend/src/components/AIConfig.vue`: AI service configuration modal
- `frontend/src/components/ArxivInput.vue`: ArXiv paper ID input component
- `frontend/src/components/ArxivHoverPopup.vue`: Hover popup for ArXiv paper previews
- `frontend/src/views/PaperList.vue`: Paper listing with search and filtering
- `frontend/src/views/PaperReader.vue`: Split-pane PDF reader + AI chat

## Data Flow

1. **Zotero Integration**: Direct local API access via `http://localhost:23119`
2. **PDF Processing**: PDF → MD5 hash → cache check → markitdown conversion → cache storage
3. **AI Analysis**: Paper content → OpenAI API → structured response → chat history
4. **Chat Persistence**: Real-time saving to SQLite with JSON serialization

## Development Workflow

1. **Start backend**: `uv run uvicorn app.main:app --reload`
2. **Start frontend**: `cd frontend && pnpm dev`
3. **Test Zotero connection**: Backend auto-detects local Zotero at startup
4. **Configure AI**: Set OpenAI-compatible API key in frontend settings

## Git Hooks (Lefthook)

Configured in `lefthook.yml`:
- Python formatting with black
- Python linting with ruff
- TypeScript formatting/linting
- Trailing whitespace cleanup
- End-of-file fixes

**Always run**:
- `uv run lefthook run pre-commit` before committing
- `git add` before `lefthook`

## Coding Style Guidelines

### Python
- **Async/await over callbacks**: Always use async/await for I/O operations
- **aiohttp for HTTP**: Use aiohttp for all external HTTP calls
- **Specific exception handling**: Never use broad `try...except` blocks
- **Type hints**: Use proper type annotations throughout
- **Black formatting**: 88 character line length
- **Ruff linting**: Follow configured linting rules

### TypeScript/Vue
- **Composition API**: Prefer Vue 3 Composition API
- **Type safety**: Strict TypeScript checking enabled
- **Tailwind CSS**: Use utility-first styling with Tailwind v4
- **Component naming**: PascalCase for components, camelCase for functions
- **File structure**: Mirror backend API structure in services

### General Patterns
- **Service layer abstraction**: All external calls go through dedicated services
- **Error boundaries**: Proper error handling at service boundaries
- **Async operations**: Never block the event loop with sync operations

## Testing

### Backend Tests
- Located in `app/tests/`
- Uses pytest-asyncio for async test support
- Run with: `uv run -m pytest -v`

### Frontend Type Checking
- Vue TypeScript checking: `pnpm type-check`
- ESLint + Prettier: `pnpm lint && pnpm format`

## Production Deployment

1. Build frontend: `cd frontend && pnpm build`
2. Backend serves static files from `frontend/dist/`
3. All API routes remain available under `/api/v1/`

## Common Troubleshooting

- **Zotero not detected**: Ensure Zotero is running and local API is enabled
- **PDF parsing issues**: Check file permissions and PDF file validity
- **CORS issues**: Verify frontend proxy config in `vite.config.ts`
