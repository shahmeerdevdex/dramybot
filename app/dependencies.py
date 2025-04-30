from app.db.session import get_session
from typing import AsyncGenerator

async def get_db() -> AsyncGenerator:
    async with get_session() as session:
        yield session
