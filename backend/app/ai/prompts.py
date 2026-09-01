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

# ── Shared rule blocks (single source of truth — edit here, not per-function) ─

VOICE_RULES = """Voice & Rhythm Rules:
1. Voice: 'Smart friend who figured something out' (authentic, helpful, specific, non-preachy). Use "I found that..." energy, not "You should..." lecturing.
2. Rhythm: 'Short. Breathe. Land.' — one idea per sentence, generous line breaks, no fluff.
3. Specificity beats vagueness. If the source has a number, date, or concrete detail, use it.
   Example: "made good revenue" -> "made $47,329". "a lot of people" -> "2,847 people".
4. Hook: open with a compelling hook (curiosity gap, contrarian observation, or high-value insight) — never with "Great question!" or a throat-clearing intro.

Example rhythm shift (apply this pattern, don't restate this exact wording):
Flat: "I spent three years building my business the wrong way before I finally realized the key was focusing on fewer things and doing them well."
Rewritten: "I built wrong for 3 years.\\n\\nThen I figured it out.\\n\\nFocus on less.\\nDo it exceptionally well."
"""

IMAGE_QUERY_RULE = """Image query rule: stock photo libraries almost never have photos of real, named
people (athletes, celebrities, politicians) — those are rights-managed, not stock. If the
content centers on a specific named person, describe the general scene, action, or emotion
instead of naming them.
Bad:  "Gabriel Jesus Barcelona stadium"  ->  Good: "footballer celebrating new contract signing"
"""

GROUNDING_RULE = (
    "Grounding: Only use facts, numbers, names, and claims that appear in the source "
    "content above. Never invent a statistic, quote, or detail to make the post sound "
    "more specific — if the source is vague, keep the claim vague rather than fabricate."
)

BANNED_PATTERNS = """Do not use, under any circumstances:
- Em dashes (—) or en dashes (–). Use commas, periods, or colons.
- Significance inflation: "stands as a testament", "marks a pivotal moment", "underscores its importance", "plays a crucial role".
- Superficial "-ing" tack-ons: "highlighting...", "showcasing...", "reflecting...", "fostering...".
- Rule-of-three synonym cycling (e.g. "a catalyst, a partner, a foundation").
- Generic openers: "Great question!", "Here's the thing:", "Let's dive in".
- Generic closers: "The future looks bright", "Exciting times ahead".
- Hedge-stacking: "could potentially be argued that... might have some effect"."""

JSON_SHAPE = """Return ONLY valid JSON, no markdown fences, no preamble, in this exact shape:
{
  "image_query": "a 3-6 word visual search phrase describing a relevant, high-quality stock photo",
  "hashtags": ["#Example", "#Tags", "#Here"],
  "caption": "the platform-formatted caption text"
}"""

SELF_CRITIQUE_STEP = """Before returning your answer: silently draft the caption, then check it line by line
against the Voice & Rhythm Rules and the banned-pattern list above. Rewrite any line that
violates either. Only output the corrected final JSON — never show the draft, the critique,
or any reasoning."""

PUNCHY_RULES = """PUNCHY MODE — override the normal caption format:
- One to three short lines. Total caption under 220 characters regardless of the platform limit.
- No setup, no explanation, no step-by-step, no "here's why" breakdown.
- Just the hook and the punchline. If it doesn't land in one breath, cut it.
- Still zero em dashes, still grounded only in the source content, still no banned patterns."""


def full_extraction_prompt(source_content: str, platform: str, char_limit: int, mode: str = "standard") -> str:
    if "You are extracting social media content from source material." in source_content:
        return source_content

    platform_guide = PLATFORM_STRATEGY.get(platform, PLATFORM_STRATEGY.get("linkedin", ""))
    mode_block = PUNCHY_RULES if mode == "punchy" else ""

    return f"""You are an elite social media copywriter and viral strategist extracting high-performing content.

Source content:
\"\"\"{source_content}\"\"\"

Target Platform: {platform.upper()}
Character Limit: Caption MUST be {char_limit} characters or fewer (including spaces & punctuation).

{VOICE_RULES}

{GROUNDING_RULE}

{IMAGE_QUERY_RULE}

{BANNED_PATTERNS}

Platform Playbook:
{platform_guide}

{mode_block}

{SELF_CRITIQUE_STEP}

{JSON_SHAPE}"""


def image_query_prompt(source_content: str) -> str:
    return f"""Extract a short 3-6 word visual search phrase for a stock photo that fits this content:

\"\"\"{source_content}\"\"\"

Important: stock photo libraries almost never have photos of real, named people
(athletes, celebrities, politicians) — those are rights-managed, not stock. If the
content is about a specific named person, describe the general scene, action, or
emotion instead of naming them.
Bad:  "Gabriel Jesus Barcelona stadium"
Good: "footballer celebrating new contract signing"
Bad:  "Taylor Swift concert tour"
Good: "pop concert crowd stage lights"

Return ONLY the phrase, nothing else."""


def hashtags_prompt(source_content: str, platform: str) -> str:
    return f"""Extract 3-5 relevant hashtags for a {platform} post based on this content:

\"\"\"{source_content}\"\"\"

Avoid generic, oversaturated tags (#success, #motivation, #hustle) unless the source content
is genuinely about that topic. Prefer specific, niche tags over broad ones.

Return ONLY a JSON array of strings, e.g. ["#Example", "#Tags"]"""


def caption_prompt(source_content: str, platform: str, char_limit: int) -> str:
    platform_guide = PLATFORM_STRATEGY.get(platform, PLATFORM_STRATEGY.get("linkedin", ""))
    return f"""You are an elite social media copywriter.
Write a high-converting {platform.upper()} caption based on this content:

\"\"\"{source_content}\"\"\"

Playbook:
{platform_guide}

{VOICE_RULES}

{GROUNDING_RULE}

{BANNED_PATTERNS}

{SELF_CRITIQUE_STEP}

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