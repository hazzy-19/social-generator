"""
Prompt templates only. One function per extraction type. No HTTP calls here.
"""

PLATFORM_STRATEGY = {
    "linkedin": (
        "LinkedIn Thought-Leadership & Direct Response:\n"
        "- Hook in first 1-2 lines before 'see more' (curiosity, contrarian take, or specific metric).\n"
        "- 'Short. Breathe. Land.' cadence: one thought per sentence, generous line breaks for scanning.\n"
        "- Break down insights with tactical pointers (e.g. ↳).\n"
        "- Peer-to-peer tone ('smart friend who figured something out'), specific > vague.\n"
        "- End with a single low-friction discussion question."
    ),
    "x": (
        "Twitter/X Viral & Punchy Style:\n"
        "- Strong pattern interrupt or contrarian hook in the opening words.\n"
        "- Fast-paced, punchy, zero fluff or corporate jargon.\n"
        "- Short lines, high emotional resonance or counter-intuitive insight.\n"
        "- Clear, scroll-stopping takeaway."
    ),
    "instagram": (
        "Instagram Visual & Engaging Style:\n"
        "- Visually evocative opening line that grabs attention immediately.\n"
        "- Story-driven or bulleted value with aesthetic spacing.\n"
        "- Strong call-to-action (Save this for later / Share with a friend).\n"
        "- Use relevant emojis naturally."
    ),
    "facebook": (
        "Facebook Community & Conversational Style:\n"
        "- Relatable, authentic storytelling with an emotional setup.\n"
        "- Conversational phrasing that invites discussion and comments.\n"
        "- Friendly, accessible, non-academic tone."
    ),
}


def full_extraction_prompt(source_content: str, platform: str, char_limit: int) -> str:
    if "You are extracting social media content from source material." in source_content:
        return source_content

    platform_guide = PLATFORM_STRATEGY.get(platform, PLATFORM_STRATEGY.get("linkedin", ""))
        
    return f"""You are an elite social media copywriter and viral strategist extracting high-performing content.

Source content:
\"\"\"{source_content}\"\"\"

Target Platform: {platform.upper()}
Character Limit: Caption MUST be {char_limit} characters or fewer (including spaces & punctuation).

Copywriting & Voice Rules:
1. Voice: 'Smart friend who figured something out' (authentic, helpful, specific, non-preachy).
2. Rhythm: 'Short. Breathe. Land.' — short sentences, intentional whitespace, zero fluff.
3. Specificity: Specific numbers and clear takeaways beat vague generic claims.
4. Hook: Open with a compelling hook (curiosity gap, contrarian observation, story beat, or high-value insight).
5. NO EM DASHES: NEVER use em dashes (—) or en dashes (–) anywhere in the output. Use commas, periods, colons, or natural line breaks instead.

Platform Playbook:
{platform_guide}

Return ONLY valid JSON, no markdown fences, no preamble, in this exact shape:
{{
  "image_query": "a 3-6 word visual search phrase describing a relevant, high-quality stock photo",
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
    platform_guide = PLATFORM_STRATEGY.get(platform, PLATFORM_STRATEGY.get("linkedin", ""))
    return f"""You are an elite social media copywriter.
Write a high-converting {platform.upper()} caption based on this content:

\"\"\"{source_content}\"\"\"

Playbook:
{platform_guide}

Voice: 'Smart friend who figured something out', 'Short. Breathe. Land.' cadence.
CRITICAL: NEVER use em dashes (—) or en dashes (–). Use commas, periods, or colons instead.
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
