from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PROJECT_NAME: str = "AIZotero"
    VERSION: str = "0.1.0"
    DEBUG: bool = True

    # CORS settings
    ALLOWED_ORIGINS: list[str] = Field(
        default=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
        ],
        description="Allowed CORS origins",
    )

    # Zotero settings
    ZOTERO_API_KEY: str = ""
    ZOTERO_USER_ID: str = ""

    # Data directory for file storage
    DATA_DIR: Path = Field(
        default=Path("data"), description="Directory for storing application data files"
    )


settings = Settings()
