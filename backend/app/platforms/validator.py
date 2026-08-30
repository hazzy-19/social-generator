"""
Validation against platform limits. Pure functions, no dependencies
outside this module.
"""


def count_chars(caption: str | None, hashtags: list[str]) -> int:
    caption_len = len(caption) if caption else 0
    hashtags_len = len(" ".join(hashtags)) if hashtags else 0
    # +1 for the space joining caption and hashtags, only if both exist
    joiner = 1 if caption and hashtags else 0
    return caption_len + hashtags_len + joiner


def is_within_limit(caption: str | None, hashtags: list[str], limit: int) -> bool:
    return count_chars(caption, hashtags) <= limit


def truncate_to_limit(caption: str, limit: int) -> str:
    """Truncates at the last full word before the limit, never mid-word."""
    if len(caption) <= limit:
        return caption
    truncated = caption[:limit]
    last_space = truncated.rfind(" ")
    return truncated[:last_space] if last_space > 0 else truncated
