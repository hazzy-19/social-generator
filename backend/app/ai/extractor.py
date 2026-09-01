"""
Public interface of the ai module. Everything else in this package
(client.py, prompts.py) is an implementation detail behind these functions.
This module never touches the database or knows about SocialGeneration.
"""
import json
import re
from dataclasses import dataclass

from app.ai import prompts
from app.ai.client import complete
from app.shared.exceptions import ExternalServiceError

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


@dataclass
class FullExtraction:
    image_query: str
    hashtags: list[str]
    caption: str
    prompt_used: str


async def extract_all(source_content: str, platform: str, char_limit: int) -> FullExtraction:
    """Single call covering image query + hashtags + caption together,
    so the three outputs stay consistent with each other."""
    prompt = prompts.full_extraction_prompt(source_content, platform, char_limit)
    try:
        raw = await complete(prompt)
        data = _parse_json(raw)
        return FullExtraction(
            image_query=data["image_query"],
            hashtags=data["hashtags"],
            caption=data["caption"],
            prompt_used=prompt,
        )
    except Exception as exc:
        print(f"WARNING: AI extraction failed, returning fallback: {exc}")
        return FullExtraction(
            image_query="A clean, professional desk setup",
            hashtags=["#technology", "#innovation", "#future", "#growth"],
            caption=f"This is a fallback generated post for {platform} based on: {source_content[:50]}... \n\nWe are currently experiencing issues reaching the AI model.\n\nDEBUG ERROR INFO: {type(exc).__name__}: {str(exc)}",
            prompt_used=prompt,
        )


async def extract_image_query(source_content: str) -> str:
    try:
        return await complete(prompts.image_query_prompt(source_content))
    except Exception as exc:
        raise ExternalServiceError(f"AI image query extraction failed: {exc}") from exc


async def extract_hashtags(source_content: str, platform: str) -> list[str]:
    try:
        raw = await complete(prompts.hashtags_prompt(source_content, platform))
        return _parse_json(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ExternalServiceError(f"AI returned unparseable hashtags: {exc}") from exc
    except ExternalServiceError:
        raise
    except Exception as exc:
        raise ExternalServiceError(f"AI hashtag extraction failed: {exc}") from exc


async def extract_caption(source_content: str, platform: str, char_limit: int) -> str:
    try:
        raw = await complete(prompts.caption_prompt(source_content, platform, char_limit))
        return sanitize_dashes(raw)
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


def _parse_json(raw: str):
    """Models occasionally wrap JSON in markdown fences despite instructions — strip if present."""
    cleaned = raw.strip()
    match = _JSON_FENCE_RE.search(cleaned)
    if match:
        cleaned = match.group(1).strip()
    data = json.loads(cleaned)
    if isinstance(data, dict):
        if "caption" in data and isinstance(data["caption"], str):
            data["caption"] = sanitize_dashes(data["caption"])
        if "image_query" in data and isinstance(data["image_query"], str):
            data["image_query"] = sanitize_dashes(data["image_query"])
        if "hashtags" in data and isinstance(data["hashtags"], list):
            data["hashtags"] = [sanitize_dashes(tag) for tag in data["hashtags"]]
    return data
