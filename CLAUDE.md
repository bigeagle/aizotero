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
- `uv run lefthook run pre-commit` - Run all git hooks
- `pnpm lint` - Lint frontend code
- `pnpm dev` - Start frontend dev server
- `pnpm build` - Build frontend for production
- `pnpm type-check` - TypeScript type checking
- `pnpm format` - Format frontend code with Prettier

## Key Files Added

- `frontend/tailwind.config.js` - Tailwind CSS configuration (v4)
- `frontend/postcss.config.js` - PostCSS configuration for Tailwind
- `frontend/src/assets/main.css` - Tailwind CSS imports and custom styles
- `app/services/pdf_parser.py` - PDF to Markdown conversion service (async with thread pool)
- `app/services/zotero_service.py` - Zotero API service (async with aiohttp)
- `app/services/arxiv_service.py` - ArXiv paper fetching service (async)
- `app/api/v1/arxiv.py` - ArXiv API endpoints
- `app/api/v1/chat.py` - AI chat API endpoints
- `app/models/arxiv.py` - ArXiv data models
- `lefthook.yml` - Git hooks for code quality (replaced pre-commit)
- `frontend/src/components/AIChat.vue` - AI chat interface component
- `frontend/src/components/AIConfig.vue` - AI configuration management component
- `frontend/src/services/aiService.ts` - AI service integration
- `frontend/src/stores/aiStore.ts` - Pinia store for AI state management
- `app/data/` - Sample data and utilities

## Project Structure

```
aizotero/
├── app/                 # FastAPI backend
│   ├── __init__.py
│   ├── main.py          # FastAPI application entry
│   ├── api/             # API routes
│   │   ├── __init__.py
│   │   └── v1/          # API version 1
│   │       ├── __init__.py
│   │       ├── papers.py      # Zotero papers API
│   │       ├── arxiv.py       # ArXiv integration API
│   │       └── chat.py        # AI chat API
│   ├── core/            # Configuration
│   │   ├── __init__.py
│   │   └── config.py    # Pydantic settings
│   ├── data/            # Sample data and utilities
│   │   ├── __init__.py
│   │   ├── sample/
│   │   └── sample_data.py
│   ├── models/          # Pydantic models
│   │   ├── __init__.py
│   │   ├── paper.py     # Paper data models
│   │   └── arxiv.py     # ArXiv data models
│   ├── services/        # Business logic
│   │   ├── __init__.py
│   │   ├── pdf_parser.py      # PDF to Markdown service
│   │   ├── zotero_service.py  # Zotero API service
│   │   └── arxiv_service.py   # ArXiv paper fetching service
│   └── tests/           # Backend tests
│       ├── __init__.py
│       └── test_main.py
├── frontend/            # Vue.js + TypeScript + Tailwind CSS frontend
│   ├── package.json     # Frontend dependencies
│   ├── pnpm-lock.yaml   # Package lock
│   ├── vite.config.ts   # Vite configuration
│   ├── tailwind.config.js # Tailwind CSS configuration
│   ├── postcss.config.js # PostCSS configuration
│   ├── tsconfig.json    # TypeScript config
│   ├── index.html       # HTML entry point
│   └── src/
│       ├── main.ts           # Vue app entry
│       ├── App.vue           # Root component
│       ├── env.d.ts          # TypeScript declarations
│       ├── router/           # Vue Router
│       │   └── index.ts
│       ├── views/            # Page components
│       │   ├── PaperList.vue
│       │   └── PaperReader.vue
│       ├── assets/           # Static assets
│       │   └── main.css      # Tailwind CSS imports
│       ├── components/       # Reusable components
│       │   ├── AIChat.vue
│       │   └── AIConfig.vue
│       ├── services/         # Service integrations
│       │   └── aiService.ts
│       ├── stores/           # Pinia stores
│       │   └── aiStore.ts
│       ├── types/            # TypeScript type definitions
│       └── utils/            # Utility functions
├── data/                  # Cache and data storage
│   └── cache/             # Application cache
├── docs/                  # Design documents
│   ├── 0001-design.md     # Project requirements
│   ├── 0002-frontend-ai-design.md # Frontend AI integration design
│   ├── 0003-zotero-connector-api.md # Zotero Connector API docs
│   └── 0004-save-arxiv-to-zotero-design.md # ArXiv integration design
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
├── pyproject.toml        # Python project configuration
├── uv.lock               # UV dependency lock
├── README.md             # Project documentation
├── lefthook.yml          # Git hooks configuration
└── CLAUDE.md             # Claude Code guidance
```

## Core Features

1. **List Page**: Display papers from Zotero, show processing status with tag filtering
2. **Reader Page**: PDF viewer on left, AI chat on right with resizable panels
3. **AI Integration**: Paper analysis and Q&A based on content with local storage persistence
4. **Zotero Sync**: Async local API integration for paper metadata
5. **Search & Filter**: Real-time search and tag-based filtering
6. **Async Processing**: Non-blocking I/O for all external operations
7. **AI Configuration**: Frontend component for managing AI API settings
8. **Caching**: PDF processing results cached in `data/cache/markitdown/`

## Quick Start Commands

```bash
# Backend
uv run uvicorn app.main:app --reload

# Frontend
cd frontend && pnpm dev

# Tests
uv run pytest -v

# Code formatting
uv run black .
uv run ruff check . --fix

# Frontend linting
cd frontend && pnpm lint
cd frontend && pnpm type-check
cd frontend && pnpm format
```

## Notice

### Git Hooks

1. After staging files with `git add`, ALWAYS run `uv run lefthook run pre-commit` to ensure code quality before committing.
2. ALWAYS run `git add` before lefthook
3. ALWAYS run lefthook before commit
4. If git commit failed because of pre-commit checking, if auto-fixed, retry withou `--amend`

### Coding Style
1. DO NOT write overly broad `try ... except` blocks that catch all exceptions.
2. Prefer async/await over callbacks, use aiohttp for HTTP
