"""
Versioned JSON store for prompt versions, evaluation results, and history.

Layout under backend/optimizer/runs/:
    prompt_v1/
        original.json       — the baseline prompt captured at run time
        candidates.json     — all compressed variants
        evaluation.json     — scores per candidate
        diff.json           — what changed vs. baseline
    active_prompt.json      — the human-approved winner (read by production optionally)
    history.json            — append-only log of every run
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Runs directory lives inside the optimizer package itself
_RUNS_DIR = Path(__file__).parent / "runs"


# ── helpers ───────────────────────────────────────────────────────────────────

def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _read(path: Path) -> Any:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write(path: Path, data: Any) -> None:
    _ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── version naming ────────────────────────────────────────────────────────────

def next_version_name() -> str:
    """Return the next unused version directory name, e.g. 'prompt_v3'."""
    existing = [
        d.name for d in _RUNS_DIR.iterdir()
        if d.is_dir() and d.name.startswith("prompt_v")
    ] if _RUNS_DIR.exists() else []
    numbers = []
    for name in existing:
        try:
            numbers.append(int(name.replace("prompt_v", "")))
        except ValueError:
            pass
    n = max(numbers) + 1 if numbers else 1
    return f"prompt_v{n}"


def list_versions() -> list[str]:
    """Return sorted list of existing version names."""
    if not _RUNS_DIR.exists():
        return []
    return sorted(
        [d.name for d in _RUNS_DIR.iterdir() if d.is_dir() and d.name.startswith("prompt_v")],
        key=lambda n: int(n.replace("prompt_v", ""))
    )


# ── save / load ───────────────────────────────────────────────────────────────

def save_original(version: str, prompt_key: str, text: str, token_count: int) -> None:
    path = _RUNS_DIR / version / "original.json"
    existing = _read(path) or {}
    existing[prompt_key] = {
        "text": text,
        "token_count": token_count,
        "captured_at": _now(),
    }
    _write(path, existing)


def save_candidates(version: str, prompt_key: str, candidates: list[dict]) -> None:
    path = _RUNS_DIR / version / "candidates.json"
    existing = _read(path) or {}
    existing[prompt_key] = candidates
    _write(path, existing)


def save_evaluation(version: str, prompt_key: str, results: list[dict]) -> None:
    path = _RUNS_DIR / version / "evaluation.json"
    existing = _read(path) or {}
    existing[prompt_key] = results
    _write(path, existing)


def save_diff(version: str, prompt_key: str, diff_data: dict) -> None:
    path = _RUNS_DIR / version / "diff.json"
    existing = _read(path) or {}
    existing[prompt_key] = diff_data
    _write(path, existing)


def load_version(version: str) -> dict:
    """Load all data for a version (original, candidates, evaluation, diff)."""
    base = _RUNS_DIR / version
    return {
        "original":   _read(base / "original.json") or {},
        "candidates": _read(base / "candidates.json") or {},
        "evaluation": _read(base / "evaluation.json") or {},
        "diff":       _read(base / "diff.json") or {},
    }


# ── active prompt ─────────────────────────────────────────────────────────────

_ACTIVE_PATH = _RUNS_DIR / "active_prompt.json"


def approve(version: str, prompt_key: str, candidate_id: str) -> dict:
    """
    Mark a candidate as the active production prompt.
    Returns the written record.
    """
    version_data = load_version(version)
    candidates = version_data["candidates"].get(prompt_key, [])
    match = next((c for c in candidates if c["id"] == candidate_id), None)
    if match is None:
        raise ValueError(f"Candidate '{candidate_id}' not found in {version}/{prompt_key}")

    active = _read(_ACTIVE_PATH) or {}
    active[prompt_key] = {
        "version": version,
        "candidate_id": candidate_id,
        "text": match["text"],
        "token_count": match["token_count"],
        "approved_at": _now(),
    }
    _write(_ACTIVE_PATH, active)

    # Append to history
    _append_history({
        "event": "approved",
        "version": version,
        "prompt_key": prompt_key,
        "candidate_id": candidate_id,
        "at": _now(),
    })
    return active[prompt_key]


def load_active_prompts() -> dict[str, str] | None:
    """
    Returns {prompt_key: text} for all approved prompts, or None if no
    active prompt has been approved yet.
    Called optionally by production code.
    """
    data = _read(_ACTIVE_PATH)
    if not data:
        return None
    return {key: entry["text"] for key, entry in data.items()}


def active_prompt_status() -> dict:
    """Return the full active_prompt.json content for display."""
    return _read(_ACTIVE_PATH) or {}


# ── history ───────────────────────────────────────────────────────────────────

_HISTORY_PATH = _RUNS_DIR / "history.json"


def _append_history(entry: dict) -> None:
    history = _read(_HISTORY_PATH) or []
    history.append(entry)
    _write(_HISTORY_PATH, history)


def append_run_history(version: str, prompt_keys: list[str], summary: dict) -> None:
    _append_history({
        "event": "run",
        "version": version,
        "prompt_keys": prompt_keys,
        "summary": summary,
        "at": _now(),
    })


def load_history() -> list[dict]:
    return _read(_HISTORY_PATH) or []
