"""
Orchestration logic. This is the only place that coordinates across
generations + ai + images + platforms modules. Routers call this,
never repository.py directly.
"""
import uuid
import os
import httpx
import aiofiles
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import extractor
from app.generations import repository
from app.generations.models import GenerationStatus, PlatformType, SocialGeneration
from app.images.client import fetch_best_image
from app.platforms.limits import get_char_limit
from app.platforms.validator import count_chars, is_within_limit
from app.shared.exceptions import NotFoundError

Section = Literal["image", "hashtags", "caption"]

UPLOAD_DIR = "uploads/images"

async def _download_image(image_url: str, generation_id: uuid.UUID) -> str | None:
    if not image_url:
        return None
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{generation_id}.jpg"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url, timeout=10.0)
            response.raise_for_status()
            
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(response.content)
                
        return f"/static/images/{filename}"
    except Exception as e:
        print(f"Failed to download image {image_url}: {e}")
        return image_url # fallback to external url if download fails


async def generate_new(db: AsyncSession, user_id: uuid.UUID, source_content: str, platform: PlatformType) -> SocialGeneration:
    """Runs the full extraction pipeline once, for a brand-new generation."""
    char_limit = get_char_limit(platform)

    extraction = await extractor.extract_all(source_content=source_content, platform=platform, char_limit=char_limit)

    image_url = await fetch_best_image(query=extraction.image_query)
    
    generation_id = uuid.uuid4()
    local_image_url = await _download_image(image_url, generation_id)

    generation = SocialGeneration(
        id=generation_id,
        user_id=user_id,
        source_content=source_content,
        platform=platform,
        image_query=extraction.image_query,
        image_url=local_image_url,
        hashtags=extraction.hashtags,
        caption=extraction.caption,
        char_limit=char_limit,
        char_count=count_chars(extraction.caption, extraction.hashtags),
        status=GenerationStatus.draft,
    )
    return await repository.create(db, generation)


async def reload_section(db: AsyncSession, user_id: uuid.UUID, generation_id: uuid.UUID, section: Section) -> SocialGeneration:
    """Re-runs exactly one section, leaves the other two + their approvals untouched."""
    generation = await _get_or_raise(db, generation_id, user_id)

    if section == "image":
        query = await extractor.extract_image_query(generation.source_content)
        generation.image_query = query
        new_image_url = await fetch_best_image(query=query)
        generation.image_url = await _download_image(new_image_url, generation.id)
        generation.image_approved = False

    elif section == "hashtags":
        generation.hashtags = await extractor.extract_hashtags(generation.source_content, generation.platform)
        generation.hashtags_approved = False

    elif section == "caption":
        generation.caption = await extractor.extract_caption(
            generation.source_content, generation.platform, generation.char_limit
        )
        generation.caption_approved = False

    generation.char_count = count_chars(generation.caption, generation.hashtags)
    return await repository.update(db, generation)


async def approve_section(db: AsyncSession, user_id: uuid.UUID, generation_id: uuid.UUID, section: Section) -> SocialGeneration:
    generation = await _get_or_raise(db, generation_id, user_id)

    if section == "image":
        generation.image_approved = True
    elif section == "hashtags":
        generation.hashtags_approved = True
    elif section == "caption":
        if not is_within_limit(generation.caption, generation.hashtags, generation.char_limit):
            raise ValueError(f"Caption exceeds {generation.char_limit} character limit for {generation.platform}")
        generation.caption_approved = True

    if generation.is_ready:
        generation.status = GenerationStatus.ready

    return await repository.update(db, generation)


async def save(db: AsyncSession, user_id: uuid.UUID, generation_id: uuid.UUID) -> SocialGeneration:
    generation = await _get_or_raise(db, generation_id, user_id)
    generation.status = GenerationStatus.saved
    return await repository.update(db, generation)


async def list_past(db: AsyncSession, user_id: uuid.UUID, platform: str | None, search: str | None, offset: int = 0) -> list[SocialGeneration]:
    return await repository.list_recent(db, user_id=user_id, platform=platform, search=search, offset=offset)


async def _get_or_raise(db: AsyncSession, generation_id: uuid.UUID, user_id: uuid.UUID) -> SocialGeneration:
    generation = await repository.get_by_id(db, generation_id, user_id)
    if generation is None:
        raise NotFoundError(f"Generation {generation_id} not found")
    return generation
