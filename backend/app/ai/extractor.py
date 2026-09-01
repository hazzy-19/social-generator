"""
Public interface of the ai module. Everything else in this package
(client.py, prompts.py) is an implementation detail behind these functions.
This module never touches the database or knows about SocialGeneration.
"""
import json
import logging
import re
from dataclasses import dataclass, field

from app.ai import prompts
from app.ai.client import complete
from app.shared.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)
_REQUIRED_KEYS = ("image_query", "hashtags", "caption")


@dataclass
class FullExtraction:
    image_query: str
    hashtags: list[str]
    caption: str
    prompt_used: str
    is_fallback: bool = False
    error: str | None = None  # populated only when is_fallback is True; never part of caption/content


async def extract_all(source_content: str, platform: str, char_limit: int, mode: str = "standard") -> FullExtraction:
    """Single call covering image query + hashtags + caption together,
    so the three outputs stay consistent with each other.

    mode: "standard" (default) or "punchy" — punchy skips explanation/setup
    and returns a short, hook-only caption regardless of char_limit.
    """
    prompt = prompts.full_extraction_prompt(source_content, platform, char_limit, mode=mode)
    try:
        raw = await complete(prompt)
        data = _parse_json(raw)
        caption = _enforce_char_limit(data["caption"], char_limit)
        return FullExtraction(
            image_query=data["image_query"],
            hashtags=data["hashtags"],
            caption=caption,
            prompt_used=prompt,
        )
    except Exception as exc:
        logger.warning("AI extraction failed, returning fallback", exc_info=exc)
        return FullExtraction(
            image_query="A clean, professional desk setup",
            hashtags=["#technology", "#innovation", "#future", "#growth"],
            caption=f"We couldn't generate a post for this content right now. "
                    f"Try again, or write your own caption for {platform}.",
            prompt_used=prompt,
            is_fallback=True,
            error=f"{type(exc).__name__}: {exc}",
        )


async def extract_image_query(source_content: str) -> str:
    try:
        raw = await complete(prompts.image_query_prompt(source_content))
        return sanitize_dashes(raw)
    except Exception as exc:
        raise ExternalServiceError(f"AI image query extraction failed: {exc}") from exc


async def extract_hashtags(source_content: str, platform: str) -> list[str]:
    try:
        raw = await complete(prompts.hashtags_prompt(source_content, platform))
        tags = _parse_json(raw)
        if not isinstance(tags, list):
            raise ExternalServiceError(f"AI hashtags response was not a list: {raw!r}")
        return [sanitize_dashes(tag) for tag in tags]
    except (json.JSONDecodeError, TypeError) as exc:
        raise ExternalServiceError(f"AI returned unparseable hashtags: {exc}") from exc
    except ExternalServiceError:
        raise
    except Exception as exc:
        raise ExternalServiceError(f"AI hashtag extraction failed: {exc}") from exc


async def extract_caption(source_content: str, platform: str, char_limit: int) -> str:
    try:
        raw = await complete(prompts.caption_prompt(source_content, platform, char_limit))
        return _enforce_char_limit(sanitize_dashes(raw), char_limit)
    except Exception as exc:
        raise ExternalServiceError(f"AI caption extraction failed: {exc}") from exc


async def optimize_source_content(source_content: str) -> str:
    try:
        raw = await complete(prompts.optimize_source_prompt(source_content))
        return sanitize_dashes(raw)
    except Exception as exc:
        raise ExternalServiceError(f"AI source optimization failed: {exc}") from exc


def sanitize_dashes(text: str) -> str:
    """Removes em dashes (—) and en dashes (–), replacing them with commas, colons, or standard hyphens."""
    if not text:
        return text
    # Replace ' — ' or ' – ' with comma or colon, and standalone dashes with commas
    cleaned = text.replace(" — ", ", ").replace(" – ", ", ")
    cleaned = cleaned.replace("—", ", ").replace("–", "-")
    # Fix any double commas or awkward spacing created
    cleaned = re.sub(r",\s*,+", ",", cleaned)
    return cleaned.strip()


def _enforce_char_limit(text: str, char_limit: int) -> str:
    """Model-reported character counts aren't reliable — truncate on a word
    boundary rather than trust the prompt instruction alone."""
    if not text or len(text) <= char_limit:
        return text
    logger.warning("AI caption exceeded char_limit (%d > %d), truncating", len(text), char_limit)
    truncated = text[:char_limit].rsplit(" ", 1)[0].rstrip(",.:;")
    return truncated


def _parse_json(raw: str):
    """Models occasionally wrap JSON in markdown fences despite instructions — strip if present."""
    cleaned = raw.strip()
    match = _JSON_FENCE_RE.search(cleaned)
    if match:
        cleaned = match.group(1).strip()
    data = json.loads(cleaned)
    if isinstance(data, dict):
        missing = [k for k in _REQUIRED_KEYS if k not in data]
        if missing:
            raise ExternalServiceError(f"AI response missing required keys: {missing}")
        if isinstance(data.get("caption"), str):
            data["caption"] = sanitize_dashes(data["caption"])
        if isinstance(data.get("image_query"), str):
            data["image_query"] = sanitize_dashes(data["image_query"])
        if isinstance(data.get("hashtags"), list):
            data["hashtags"] = [sanitize_dashes(tag) for tag in data["hashtags"]]
    return data