"""
HTTP layer only. Every endpoint calls a service function and returns
its result — no business logic lives here.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.generations import service
from app.generations.schemas import GenerationCreateRequest, GenerationListItem, GenerationResponse, OptimizeSourceRequest, OptimizeSourceResponse, GenerationUpdateRequest
from app.generations.service import Section
from app.platforms.types import PlatformType
from app.shared.exceptions import ExternalServiceError, NotFoundError, RateLimitedError
from app.ai import extractor

router = APIRouter(prefix="/generations", tags=["generations"])


@router.post("/optimize-source", response_model=OptimizeSourceResponse)
async def optimize_source(payload: OptimizeSourceRequest, current_user: User = Depends(get_current_user)):
    try:
        extractor.check_rate_limit(str(current_user.id))
        optimized = await extractor.optimize_source_content(payload.source_content)
        extractor.record_call(str(current_user.id))
        return OptimizeSourceResponse(optimized_content=optimized)
    except RateLimitedError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))


from fastapi.responses import StreamingResponse

@router.post("", status_code=201)
async def create_generation(payload: GenerationCreateRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        extractor.check_rate_limit(str(current_user.id))
        return StreamingResponse(
            service.stream_generation(db, current_user.id, payload.source_content, payload.platform),
            media_type="text/event-stream"
        )
    except RateLimitedError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/{generation_id}/reload/{section}", response_model=GenerationResponse)
async def reload_section(generation_id: uuid.UUID, section: Section, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        extractor.check_rate_limit(str(current_user.id))
        result = await service.reload_section(db, current_user.id, generation_id, section)
        extractor.record_call(str(current_user.id))
        return result
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RateLimitedError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/{generation_id}/approve/{section}", response_model=GenerationResponse)
async def approve_section(generation_id: uuid.UUID, section: Section, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return await service.approve_section(db, current_user.id, generation_id, section)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/{generation_id}/save", response_model=GenerationResponse)
async def save_generation(generation_id: uuid.UUID, payload: GenerationUpdateRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return await service.save(db, current_user.id, generation_id, payload.model_dump(exclude_unset=True))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("", response_model=list[GenerationListItem])
async def list_generations(
    platform: PlatformType | None = Query(default=None),
    search: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.list_past(db, current_user.id, platform=platform, search=search, offset=offset)


@router.get("/{generation_id}", response_model=GenerationResponse)
async def get_generation(generation_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return await service.get_generation(db, current_user.id, generation_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{generation_id}", status_code=204)
async def delete_generation(generation_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        await service.delete_generation(db, current_user.id, generation_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
