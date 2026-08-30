"""
ORM model only. No query logic — that lives in repository.py.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Enum, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base
from app.platforms.types import PlatformType


class GenerationStatus(str, enum.Enum):
    draft = "draft"
    ready = "ready"
    saved = "saved"


class SocialGeneration(Base):
    __tablename__ = "social_generations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_content: Mapped[str] = mapped_column(Text, nullable=False)
    platform: Mapped[PlatformType] = mapped_column(Enum(PlatformType, name="platform_type"), nullable=False)

    image_query: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text)
    image_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    hashtags: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    hashtags_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    caption: Mapped[str | None] = mapped_column(Text)
    caption_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    char_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    char_count: Mapped[int | None] = mapped_column(Integer)

    status: Mapped[GenerationStatus] = mapped_column(
        Enum(GenerationStatus, name="generation_status"), default=GenerationStatus.draft, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    @property
    def is_ready(self) -> bool:
        return self.image_approved and self.hashtags_approved and self.caption_approved
