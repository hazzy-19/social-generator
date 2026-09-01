"""
Prompt compressor: generates multiple compressed candidates at three
aggressiveness levels.

Levels:
  conservative  — removes only redundant/low-impact items, merges duplicates.
                  Safest; minimal behavioural risk.
  moderate      — also rewrites verbose prose into tight directives.
                  Good balance for most cases.
  aggressive    — maximum compression; keeps only essential + structural items.
                  Higher risk; validate carefully before approving.

Each candidate is produced by a single LLM call with a carefully
constrained compression meta-prompt. The compressor never removes
instructions labeled 'essential' or 'structural'.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from optimizer.analyzer import AnalyzedInstruction
from optimizer.token_counter import count_tokens

Level = Literal["conservative", "moderate", "aggressive"]

LEVELS: list[Level] = ["conservative", "moderate", "aggressive"]


@dataclass
class Candidate:
    id: str              # e.g. "conservative", "moderate", "aggressive"
    level: Level
    text: str
    token_count: int

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "level": self.level,
            "text": self.text,
            "token_count": self.token_count,
        }


def _compression_meta_prompt(
    original: str,
    instructions: list[AnalyzedInstruction],
    level: Level,
) -> str:
    # Build a summary of what to keep / drop at this level
    keep_labels = {
        "conservative": {"essential", "structural", "ambiguous"},
        "moderate":     {"essential", "structural"},
        "aggressive":   {"essential", "structural"},
    }[level]

    drop_labels = {
        "conservative": {"redundant", "low-impact"},
        "moderate":     {"redundant", "low-impact", "ambiguous"},
        "aggressive":   {"redundant", "low-impact", "ambiguous", "conflicting"},
    }[level]

    rewrite_note = {
        "conservative": "Keep wording close to the original. Only remove clearly redundant or low-impact instructions.",
        "moderate":     "Rewrite verbose prose into tight, direct directives. Merge overlapping rules. Remove all redundant/low-impact/ambiguous items.",
        "aggressive":   "Maximally compress. Use the fewest words possible while preserving all essential behavior and output format. Remove all non-essential content.",
    }[level]

    keep_items = "\n".join(
        f"  - {i.text[:100]}"
        for i in instructions if i.label in keep_labels
    )
    drop_items = "\n".join(
        f"  - [{i.label}] {i.text[:100]}"
        for i in instructions if i.label in drop_labels
    )

    return f"""You are a prompt compression expert. Compress the following AI prompt at {level.upper()} aggressiveness.

ORIGINAL PROMPT:
\"\"\"
{original}
\"\"\"

INSTRUCTIONS TO KEEP (do not remove these):
{keep_items or "  (all are droppable at this level)"}

INSTRUCTIONS TO REMOVE OR MERGE:
{drop_items or "  (none)"}

COMPRESSION RULES:
- {rewrite_note}
- Do NOT convert everything to bullet points blindly. Optimize for model comprehension and behavior.
- Do NOT add anything new — only compress what is there.
- Resolve conflicting instructions by keeping the stricter / more specific one.
- Preserve all output format requirements exactly (JSON shape, field names, etc.).
- Do NOT explain your changes. Return ONLY the compressed prompt text, nothing else."""


async def compress(
    prompt_key: str,
    original_text: str,
    instructions: list[AnalyzedInstruction],
    llm_complete_fn,
) -> list[Candidate]:
    """
    Generate one compressed candidate per aggressiveness level.
    Returns a list of Candidate objects (3 total).
    """
    candidates = []
    for level in LEVELS:
        meta = _compression_meta_prompt(original_text, instructions, level)
        compressed_text = await llm_complete_fn(meta, max_tokens=1200)
        compressed_text = compressed_text.strip()
        candidates.append(Candidate(
            id=level,
            level=level,
            text=compressed_text,
            token_count=count_tokens(compressed_text),
        ))
    return candidates


def format_candidates_report(
    prompt_key: str,
    original_tokens: int,
    candidates: list[Candidate],
) -> str:
    from optimizer.token_counter import format_reduction

    lines = [
        f"{'-'*60}",
        f"  COMPRESSED CANDIDATES --- {prompt_key}",
        f"{'-'*60}",
        f"  Original : {original_tokens:,} tokens",
        "",
    ]
    for c in candidates:
        red = format_reduction(original_tokens, c.token_count)
        lines.append(f"  [{c.id.upper():<14}]  {c.token_count:,} tokens  {red}")

    lines.append(f"{'-'*60}")
    return "\n".join(lines)
