import asyncio
from app.core.database import engine, Base
from app.generations.models import SocialGeneration

async def drop():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=[SocialGeneration.__table__])

if __name__ == "__main__":
    asyncio.run(drop())
