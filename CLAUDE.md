# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered paper reading assistant for Zotero with web interface. Helps users quickly understand and manage research papers through AI-driven analysis and chat interface.

## Architecture

- **Backend**: Python + FastAPI + pyzotero
- **Frontend**: Vue.js + TypeScript + Tailwind CSS v4
- **Data Source**: Zotero local API
- **AI Integration**: OpenAI compatible API support
- **PDF Processing**: markitdown for PDF → Markdown conversion
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
- `pnpm lint` - Lint frontend code
- `pnpm dev` - Start frontend dev server
- `pnpm build` - Build frontend for production

## Key Files Added

- `frontend/tailwind.config.js` - Tailwind CSS configuration (v4)
- `frontend/postcss.config.js` - PostCSS configuration for Tailwind
- `frontend/src/assets/main.css` - Tailwind CSS imports and custom styles
- `app/services/pdf_parser.py` - PDF to Markdown conversion service
- `.pre-commit-config.yaml` - Pre-commit hooks for code quality

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
│   │       └── papers.py
│   ├── core/            # Configuration
│   │   ├── __init__.py
│   │   └── config.py    # Pydantic settings
│   ├── models/          # Pydantic models
│   │   ├── __init__.py
│   │   └── paper.py     # Paper data models
│   ├── services/        # Business logic
│   │   ├── __init__.py
│   │   └── pdf_parser.py # PDF to Markdown service
│   └── tests/           # Backend tests
│       ├── __init__.py
│       └── test_main.py
├── frontend/            # Vue.js + TypeScript + Tailwind CSS frontend
│   ├── package.json     # Frontend dependencies
│   ├── pnpm-lock.yaml   # Package lock
│   ├── vite.config.ts   # Vite configuration
│   ├── tsconfig.json    # TypeScript config
│   └── src/
│       ├── __init__.py
│       ├── main.ts           # Vue app entry
│       ├── App.vue           # Root component
│       ├── env.d.ts          # TypeScript declarations
│       ├── router/           # Vue Router
│       │   └── index.ts
│       ├── views/            # Page components
│       │   ├── PaperList.vue
│       │   └── PaperReader.vue
│       ├── assets/           # Static assets
│       │   └── main.css
│       ├── components/       # Reusable components
│       ├── stores/           # Pinia stores
│       └── utils/            # Utility functions
├── docs/                  # Design documents
│   └── 0001-design.md     # Project requirements
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
├── pyproject.toml        # Python project configuration
├── uv.lock               # UV dependency lock
├── README.md             # Project documentation
└── CLAUDE.md             # Claude Code guidance
```

## Core Features

1. **List Page**: Display papers from Zotero, show processing status
2. **Reader Page**: PDF viewer on left, AI chat on right
3. **AI Integration**: Paper analysis and Q&A based on content
4. **Zotero Sync**: Local API integration for paper metadata

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
```
