import json
from typing import Any

import aiosqlite

from app.core.config import settings


class ChatDatabase:
    def __init__(self):
        self.db_path = settings.DATA_DIR / "chat_history.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        """Initialize database with simple JSON storage table"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_history (
                    paper_id TEXT PRIMARY KEY,
                    chat_data JSON NOT NULL DEFAULT '[]'
                )
                """
            )
            await db.commit()

    async def get_chat(self, paper_id: str) -> list[dict[str, Any]]:
        """Get chat history for a paper"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT chat_data FROM chat_history WHERE paper_id = ?", (paper_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return []

    async def save_chat(self, paper_id: str, chat_data: list[dict[str, Any]]) -> None:
        """Save chat history for a paper"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO chat_history (paper_id, chat_data)
                VALUES (?, ?)
                """,
                (paper_id, json.dumps(chat_data)),
            )
            await db.commit()

    async def delete_chat(self, paper_id: str) -> None:
        """Delete chat history for a paper"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM chat_history WHERE paper_id = ?", (paper_id,))
            await db.commit()

    async def get_all_chats(self) -> dict[str, list[dict[str, Any]]]:
        """Get all chat histories"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT paper_id, chat_data FROM chat_history"
            ) as cursor:
                rows = await cursor.fetchall()
                return {row[0]: json.loads(row[1]) for row in rows}
