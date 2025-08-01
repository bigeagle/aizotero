from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.papers import router as papers_router

app = FastAPI(
    title="AIZotero",
    description="AI-powered paper reading assistant for Zotero",
    version="0.1.0",
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
