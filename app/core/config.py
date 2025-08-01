from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "AIZotero"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Zotero settings
    ZOTERO_API_KEY: str = ""
    ZOTERO_USER_ID: str = ""
    
    class Config:
        env_file = ".env"


settings = Settings()