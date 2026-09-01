"""
Prompt analyzer: breaks a prompt into individual instructions and
classifies each one.

Classification labels:
  essential    — must be kept; removing it would break behavior
  redundant    — duplicates another instruction already present
  low-impact   — adds little beyond what the model would do by default
  conflicting  — contradicts another instruction in the same prompt
  structural   — format/output-shape directive (JSON, field names, etc.)
  ambiguous    — unclear meaning; could be interpreted multiple ways

The LLM is asked to return a structured JSON result; we parse and
return it as a list of AnalyzedInstruction dataclasses.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Literal

ClassLabel = Literal["essential", "redundant", "low-impact", "conflicting", "structural", "ambiguous"]

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


@dataclass
class AnalyzedInstruction:
    text: str
    label: ClassLabel
    reason: str
    overlap_with: list[str]  # indices of other instructions this overlaps with


def _parse_json(raw: str) -> Any:
    cleaned = raw.strip()
    m = _JSON_FENCE_RE.search(cleaned)
    if m:
        cleaned = m.group(1).strip()
    else:
        # Fallback: try to find the first '[' or '{' and the last ']' or '}'
        start = cleaned.find('[')
        end = cleaned.rfind(']')
        if start != -1 and end != -1 and start < end:
            cleaned = cleaned[start:end+1]
        else:
            start = cleaned.find('{')
            end = cleaned.rfind('}')
            if start != -1 and end != -1 and start < end:
                cleaned = cleaned[start:end+1]
    return json.loads(cleaned)


def _analysis_meta_prompt(prompt_text: str) -> str:
    return f"""You are a prompt engineering expert. Analyze the following AI prompt and break it into individual instructions.

PROMPT TO ANALYZE:
\"\"\"
{prompt_text}
\"\"\"

For each distinct instruction or directive in the prompt, output a JSON object with:
- "text": the exact instruction text (or a concise paraphrase)
- "label": one of exactly: essential | redundant | low-impact | conflicting | structural | ambiguous
- "reason": one sentence explaining the label
- "overlap_with": list of 0-based indices of other instructions this overlaps or duplicates

Label definitions:
- essential: removing it would meaningfully change or break model behavior
- redundant: duplicates or heavily overlaps another instruction
- low-impact: the model would likely behave the same without it
- conflicting: contradicts or creates tension with another instruction
- structural: specifies output format, shape, or schema
- ambiguous: unclear or could be interpreted multiple ways

Return ONLY a valid JSON array. No markdown, no preamble, no explanation.
Example: [{{"text": "...", "label": "essential", "reason": "...", "overlap_with": []}}]"""


async def analyze(prompt_text: str, llm_complete_fn) -> list[AnalyzedInstruction]:
    """
    Analyze *prompt_text* using *llm_complete_fn* (same signature as client.complete).
    Returns a list of classified instructions.
    """
    meta = _analysis_meta_prompt(prompt_text)
    raw = await llm_complete_fn(meta, max_tokens=8192)
    data = _parse_json(raw)
    return [
        AnalyzedInstruction(
            text=item["text"],
            label=item["label"],
            reason=item["reason"],
            overlap_with=item.get("overlap_with", []),
        )
        for item in data
    ]


def format_analysis_report(instructions: list[AnalyzedInstruction]) -> str:
    """Return a human-readable analysis table."""
    label_counts: dict[str, int] = {}
    for inst in instructions:
        label_counts[inst.label] = label_counts.get(inst.label, 0) + 1

    lines = [
        f"{'-'*70}",
        f"  INSTRUCTION ANALYSIS  ({len(instructions)} instructions found)",
        f"{'-'*70}",
    ]
    for i, inst in enumerate(instructions):
        overlap = f"  ⟷ overlaps #{', #'.join(str(o) for o in inst.overlap_with)}" if inst.overlap_with else ""
        lines.append(f"  #{i:2d}  [{inst.label.upper():<12}]  {inst.text[:70]}")
        lines.append(f"       Reason: {inst.reason}{overlap}")
        lines.append("")

    lines.append(f"{'-'*70}")
    lines.append("  SUMMARY:")
    for label, count in sorted(label_counts.items()):
        lines.append(f"    {label:<14} {count}")
    lines.append(f"{'-'*70}")
    return "\n".join(lines)
