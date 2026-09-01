"""
Request/response models only. No logic, no DB access.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.generations.models import GenerationStatus, PlatformType


class GenerationCreateRequest(BaseModel):
    source_content: str = Field(..., max_length=50_000)
    platform: PlatformType

class OptimizeSourceRequest(BaseModel):
    source_content: str = Field(..., max_length=50_000)


class OptimizeSourceResponse(BaseModel):
    optimized_content: str


class GenerationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_content: str
    platform: PlatformType

    image_query: str | None
    image_url: str | None
    image_approved: bool

    hashtags: list[str]
    hashtags_approved: bool

    caption: str | None
    caption_approved: bool

    char_limit: int
    char_count: int | None

    status: GenerationStatus
    created_at: datetime
    updated_at: datetime


class GenerationListItem(BaseModel):
    """Slim shape for the Past Generations list — avoids shipping full source_content."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    platform: PlatformType
    caption: str | None
    image_url: str | None
    status: GenerationStatus
    created_at: datetime
