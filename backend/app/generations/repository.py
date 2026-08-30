"""
DB queries only. No business logic, no calls to ai/ or images/ modules.
Services call these functions — repository never calls services.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.generations.models import SocialGeneration


async def create(db: AsyncSession, generation: SocialGeneration) -> SocialGeneration:
    db.add(generation)
    await db.commit()
    await db.refresh(generation)
    return generation


async def get_by_id(db: AsyncSession, generation_id: uuid.UUID) -> SocialGeneration | None:
    result = await db.execute(select(SocialGeneration).where(SocialGeneration.id == generation_id))
    return result.scalar_one_or_none()


async def list_recent(
    db: AsyncSession,
    platform: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[SocialGeneration]:
    query = select(SocialGeneration).order_by(SocialGeneration.created_at.desc()).limit(limit).offset(offset)
    if platform:
        query = query.where(SocialGeneration.platform == platform)
    if search:
        # Escape LIKE wildcards so user input can't craft expensive scan patterns.
        safe = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.where(SocialGeneration.caption.ilike(f"%{safe}%"))
    result = await db.execute(query)
    return list(result.scalars().all())


async def update(db: AsyncSession, generation: SocialGeneration) -> SocialGeneration:
    await db.commit()
    await db.refresh(generation)
    return generation


async def delete(db: AsyncSession, generation: SocialGeneration) -> None:
    await db.delete(generation)
    await db.commit()
