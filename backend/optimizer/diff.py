"""
Diff utilities: show exactly what changed between two prompt versions.

Produces both a unified text diff and a structured summary of
instructions added, removed, or changed — so you can see precisely
what the optimizer did.
"""
from __future__ import annotations

import difflib
from typing import Any


def unified_diff(original: str, optimized: str, label_a: str = "original", label_b: str = "optimized") -> str:
    """Return a unified diff string between two prompt texts."""
    a_lines = original.splitlines(keepends=True)
    b_lines = optimized.splitlines(keepends=True)
    diff = difflib.unified_diff(a_lines, b_lines, fromfile=label_a, tofile=label_b, lineterm="")
    return "".join(diff) or "(no differences)"


def side_by_side_summary(original: str, optimized: str) -> dict:
    """
    Return a structured summary of what changed:
    {
        "lines_removed": int,
        "lines_added": int,
        "chars_removed": int,
        "chars_added": int,
        "removed_lines": [...],
        "added_lines": [...],
    }
    """
    a_lines = original.splitlines()
    b_lines = optimized.splitlines()

    removed = [l for l in a_lines if l.strip() and l not in b_lines]
    added   = [l for l in b_lines if l.strip() and l not in a_lines]

    return {
        "lines_original": len(a_lines),
        "lines_optimized": len(b_lines),
        "lines_removed": len(removed),
        "lines_added": len(added),
        "chars_original": len(original),
        "chars_optimized": len(optimized),
        "removed_lines": removed,
        "added_lines": added,
    }


def format_diff_report(version_a: str, version_b: str, prompt_key: str,
                        original: str, optimized: str,
                        original_tokens: int, optimized_tokens: int) -> str:
    """Return a human-readable diff report string for printing."""
    from optimizer.token_counter import format_reduction

    summary = side_by_side_summary(original, optimized)
    udiff = unified_diff(original, optimized, label_a=version_a, label_b=version_b)

    lines = [
        f"{'-'*60}",
        f"  Prompt : {prompt_key}",
        f"  {version_a} → {version_b}",
        f"{'-'*60}",
        f"  Tokens : {original_tokens:,} → {optimized_tokens:,}  "
        f"({format_reduction(original_tokens, optimized_tokens)})",
        f"  Chars  : {summary['chars_original']:,} → {summary['chars_optimized']:,}",
        f"  Lines  : {summary['lines_original']} → {summary['lines_optimized']}  "
        f"(-{summary['lines_removed']} / +{summary['lines_added']})",
        "",
        "  UNIFIED DIFF:",
        "",
    ]
    for dl in udiff.splitlines():
        lines.append(f"  {dl}")

    return "\n".join(lines)
