"""
Prompt templates only. One function per extraction type. No HTTP calls here.
"""

PLATFORM_TONE = {
    "instagram": "catchy, visually evocative, high-energy, hashtag-friendly, use emojis",
    "linkedin": "hook-driven, thought-provoking, polarizing but professional, engaging",
    "x": "punchy, controversial hook, baiting, fast-paced, no fluff",
    "facebook": "conversational, community-engaging, relatable, attention-grabbing hooks",
}


def full_extraction_prompt(source_content: str, platform: str, char_limit: int) -> str:
    if "You are extracting social media content from source material." in source_content:
        return source_content
        
    return f"""You are extracting social media content from source material.

Source content:
\"\"\"{source_content}\"\"\"

Target platform: {platform} ({PLATFORM_TONE.get(platform, "")})
Caption MUST be {char_limit} characters or fewer, including spaces and punctuation.

Return ONLY valid JSON, no markdown fences, no preamble, in this exact shape:
{{
  "image_query": "a 3-6 word visual search phrase describing an image that fits this content",
  "hashtags": ["#Example", "#Tags", "#Here"],
  "caption": "the platform-formatted caption text"
}}"""


def image_query_prompt(source_content: str) -> str:
    return f"""Extract a short 3-6 word visual search phrase for a stock photo that fits this content:

\"\"\"{source_content}\"\"\"

Return ONLY the phrase, nothing else."""


def hashtags_prompt(source_content: str, platform: str) -> str:
    return f"""Extract 3-5 relevant hashtags for a {platform} post based on this content:

\"\"\"{source_content}\"\"\"

Return ONLY a JSON array of strings, e.g. ["#Example", "#Tags"]"""


def caption_prompt(source_content: str, platform: str, char_limit: int) -> str:
    return f"""Write a {platform} caption ({PLATFORM_TONE.get(platform, "")}) based on this content:

\"\"\"{source_content}\"\"\"

MUST be {char_limit} characters or fewer, including spaces and punctuation.
Return ONLY the caption text, nothing else."""
def optimize_source_prompt(source_content: str) -> str:
    return f"""Rewrite the following draft text to be clear, concise, and highly effective as source material for a social media post. Do not generate the post itself, just clean up the raw thoughts/notes into a coherent summary.

Source content:
\"\"\"{source_content}\"\"\"

Return ONLY the optimized text, with no introductory phrases or conversational preamble."""


# ── Optimizer integration (opt-in only) ──────────────────────────────────────
# The offline prompt optimizer writes approved prompts to
# optimizer/runs/active_prompt.json. Production code does NOT use this
# by default. If you want to switch to an approved optimized prompt,
# call load_active_prompt() and use the returned text instead of the
# template functions above.

def load_active_prompt(prompt_key: str) -> str | None:
    """
    Returns the optimizer-approved prompt text for *prompt_key*, or None
    if no prompt has been approved yet for that key.

    Valid keys: "full_extraction", "caption", "hashtags", "image_query"

    Example usage in extractor.py:
        active = load_active_prompt("full_extraction")
        prompt_text = active or full_extraction_prompt(source_content, platform, char_limit)
    """
    try:
        from pathlib import Path
        import json
        active_path = Path(__file__).parent.parent.parent / "optimizer" / "runs" / "active_prompt.json"
        if not active_path.exists():
            return None
        with open(active_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        entry = data.get(prompt_key)
        return entry["text"] if entry else None
    except Exception:
        return None  # never crash production over an optimizer file
