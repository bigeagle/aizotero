from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.v1.papers import router as papers_router
from app.core.config import settings
from app.services.database import ChatDatabase


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI"""
    # Initialize database on startup
    chat_db = ChatDatabase()
    await chat_db.initialize()
    yield
    # Cleanup can be added here if needed


app = FastAPI(
    title="AIZotero",
    description="AI-powered paper reading assistant for Zotero",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(papers_router, prefix="/api/v1", tags=["papers"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "AIZotero is running"}


# Fallback route for static files
@app.get("/{file_path:path}")
async def serve_static_files(file_path: str):
    """Serve static files from STATIC_DIR with fallback to index.html"""
    static_dir = settings.STATIC_DIR
    requested_path = static_dir / file_path

    # If path is empty or directory, serve index.html
    if requested_path.is_dir():
        index_path = requested_path / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        else:
            raise HTTPException(status_code=404, detail="File not found")

    # If it's a file, serve the file
    if requested_path.exists() and requested_path.is_file():
        return FileResponse(requested_path)

    # Fallback to '/index.html'
    return FileResponse(static_dir / "index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
