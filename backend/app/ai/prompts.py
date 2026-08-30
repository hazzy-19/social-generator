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
