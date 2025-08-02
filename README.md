# AI Paper Assistant - AIZotero

An AI-powered paper reading assistant for Zotero with a web interface that helps users quickly understand and manage research papers.

## Features

- **Zotero Integration**: Direct connection to local Zotero library without manual import
- **AI-Driven**: Intelligent analysis of paper content with deep insights
- **Conversational Learning**: Discuss papers with AI while reading
- **Web Interface**: Modern responsive design
- **SQLite Storage**: Local storage of AI chat records with cross-session persistence
- **Real-time Search**: Multi-dimensional search by title, abstract, tags, etc.
- **PDF Preview**: Built-in PDF reader with draggable layout adjustment
- **KaTeX Support**: Perfect rendering of mathematical formulas in papers

## Quick Start

### Requirements

- Python 3.13+
- Node.js 18+
- Zotero 7+ (installed and configured)
- UV (Python package manager, recommended)
- PNPM (Node.js package manager, recommended)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd aizotero

# Install backend dependencies with UV (recommended)
uv sync

# Or use pip
pip install -r requirements.txt

# Install frontend dependencies
cd frontend && pnpm install
```

### Development

```bash
# Start backend (port 8000)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (port 5173)
pnpm dev
```

Visit http://localhost:5173 to get started

### Production Build

```bash
# Build frontend
cd frontend && pnpm build

# Backend automatically serves static files from frontend/dist
```

## Usage Guide

1. **Configure AI Service**: Configure OpenAI-compatible API key and service URL on first use
2. **Connect Zotero**: Automatically detect local Zotero library
3. **Browse Papers**: View all papers on the list page with real-time search and tag filtering
4. **Start Reading**: Click paper to enter reading interface
5. **AI Conversation**: Discuss paper content with AI on the right side, chat records are automatically saved
6. **Export Conversation**: Export AI conversations as Markdown format

## Technical Architecture

- **Backend**: FastAPI + SQLite + aiohttp (async architecture)
- **Frontend**: Vue 3 + TypeScript + Tailwind CSS v4
- **Storage**: SQLite database for AI chat record storage
- **PDF Processing**: markitdown + ThreadPoolExecutor (async conversion)
- **AI Service**: OpenAI-compatible API + KaTeX mathematical formula rendering

## Development

### Project Structure

```
aizotero/
├── app/           # FastAPI backend
├── frontend/      # Vue.js frontend
├── docs/          # Design documents
└── tests/         # Test files
```

### Common Commands

```bash
# Run tests
uv run pytest -v

# Code formatting
uv run black .
uv run ruff check . --fix

# Frontend checks and builds
cd frontend
pnpm lint
pnpm build
```

## Contributing

Welcome to submit Issues and Pull Requests!

## License

MIT License
