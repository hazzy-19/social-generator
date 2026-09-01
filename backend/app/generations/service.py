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
from app.shared.exceptions import NotFoundError, ExternalServiceError

Section = Literal["image", "hashtags", "caption"]

UPLOAD_DIR = "uploads/images"

import json
from typing import AsyncGenerator

async def stream_generation(db: AsyncSession, user_id: uuid.UUID, source_content: str, platform: PlatformType) -> AsyncGenerator[str, None]:
    """Runs the full extraction pipeline once, yielding SSE status updates, for a brand-new generation."""
    try:
        char_limit = get_char_limit(platform)
        from app.ai import prompts
        from app.ai.client import complete_stream
        from app.ai.extractor import _parse_json, FullExtraction
        
        prompt = prompts.full_extraction_prompt(source_content, platform, char_limit)
        
        yield f"data: {json.dumps({'status': 'prompt_ready', 'prompt': prompt})}\n\n"
        
        yield f"data: {json.dumps({'status': 'connecting', 'message': 'Connecting to AI model...'})}\n\n"
        
        # 1. Stream tokens from the model
        raw_response = ""
        try:
            async for chunk in complete_stream(prompt, max_tokens=700):
                raw_response += chunk
                yield f"data: {json.dumps({'status': 'thinking', 'chunk': chunk})}\n\n"
        except Exception as exc:
            err_str = str(exc)
            if "429" in err_str:
                raise ExternalServiceError("The AI model rate limit has been exceeded. Please wait a few seconds and try again.") from exc
            raise ExternalServiceError(f"AI extraction failed: {err_str}") from exc
            
        yield f"data: {json.dumps({'status': 'generating_image', 'message': 'AI finished thinking! Fetching related image...'})}\n\n"
        
        # 2. Parse response
        try:
            data = _parse_json(raw_response)
            extraction = FullExtraction(
                image_query=data["image_query"],
                hashtags=data["hashtags"],
                caption=data["caption"],
                prompt_used=prompt,
            )
        except Exception as exc:
            print(f"WARNING: AI extraction parsing failed, returning fallback: {exc}")
            extraction = FullExtraction(
                image_query="A clean, professional desk setup",
                hashtags=["#technology", "#innovation", "#future", "#growth"],
                caption=f"This is a fallback generated post for {platform} based on: {source_content[:50]}... \n\nWe experienced issues parsing the AI output.\n\nRAW DUMP: {raw_response}",
                prompt_used=prompt,
            )
        
        generation_id = uuid.uuid4()
        local_image_url = await fetch_best_image(query=extraction.image_query, generation_id=generation_id)
        
        yield f"data: {json.dumps({'status': 'saving', 'message': 'Saving to database...'})}\n\n"

        generation = SocialGeneration(
            id=generation_id,
            user_id=user_id,
            source_content=extraction.prompt_used,
            platform=platform,
            image_query=extraction.image_query,
            image_url=local_image_url,
            hashtags=extraction.hashtags,
            caption=extraction.caption,
            char_limit=char_limit,
            char_count=count_chars(extraction.caption, extraction.hashtags),
            status=GenerationStatus.draft,
        )
        saved_gen = await repository.create(db, generation)
        
        # We need a Pydantic dict to safely serialize it or construct the data manually
        # Assuming GenerationResponse structure matches this
        yield f"data: {json.dumps({'status': 'complete', 'data': {'id': str(saved_gen.id), 'source_content': saved_gen.source_content, 'platform': saved_gen.platform, 'caption': saved_gen.caption, 'hashtags': saved_gen.hashtags, 'image_url': saved_gen.image_url, 'image_approved': saved_gen.image_approved, 'caption_approved': saved_gen.caption_approved, 'hashtags_approved': saved_gen.hashtags_approved}})}\n\n"
    
    except Exception as exc:
        yield f"data: {json.dumps({'status': 'error', 'message': f'Error during generation: {str(exc)}'})}\n\n"


async def reload_section(db: AsyncSession, user_id: uuid.UUID, generation_id: uuid.UUID, section: Section) -> SocialGeneration:
    """Re-runs exactly one section, leaves the other two + their approvals untouched."""
    generation = await _get_or_raise(db, generation_id, user_id)

    if section == "image":
        query = await extractor.extract_image_query(generation.source_content)
        generation.image_query = query
        generation.image_url = await fetch_best_image(query=query, generation_id=generation.id)
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
