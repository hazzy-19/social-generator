"""
Evaluator: runs each prompt candidate against a fixed test dataset,
scores outputs using an LLM judge, and selects the best candidate.

Scoring rubric (weights sum to 1.0):
  output_quality       0.25  — is the output actually good social content?
  instruction_follow   0.25  — did the model follow all prompt constraints?
  relevance            0.15  — is the output relevant to the input?
  naturalness          0.15  — does it read naturally (no awkward AI-isms)?
  engagement_potential 0.10  — would this perform well on the platform?
  consistency          0.10  — same style/quality across test cases?

Optimization objective: quality_per_token = weighted_score / token_count

A candidate is only accepted (over the baseline) if:
  weighted_score >= baseline_score - QUALITY_THRESHOLD

Default QUALITY_THRESHOLD = 0.3  (on a 0–10 scale)
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

QUALITY_THRESHOLD = 0.3   # how much quality drop we tolerate vs. baseline

_WEIGHTS = {
    "output_quality":       0.25,
    "instruction_follow":   0.25,
    "relevance":            0.15,
    "naturalness":          0.15,
    "engagement_potential": 0.10,
    "consistency":          0.10,
}

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


# ── data structures ────────────────────────────────────────────────────────────

@dataclass
class TestCase:
    id: str
    source_content: str
    platform: str
    expected_traits: list[str]


@dataclass
class ScoreBreakdown:
    output_quality: float
    instruction_follow: float
    relevance: float
    naturalness: float
    engagement_potential: float
    consistency: float

    @property
    def weighted(self) -> float:
        total = 0.0
        for metric, weight in _WEIGHTS.items():
            total += getattr(self, metric) * weight
        return round(total, 3)


@dataclass
class CandidateResult:
    candidate_id: str       # "original", "conservative", "moderate", "aggressive"
    token_count: int
    per_case_scores: list[ScoreBreakdown] = field(default_factory=list)
    per_case_outputs: list[str] = field(default_factory=list)

    @property
    def average_score(self) -> float:
        if not self.per_case_scores:
            return 0.0
        return round(sum(s.weighted for s in self.per_case_scores) / len(self.per_case_scores), 3)

    @property
    def quality_per_token(self) -> float:
        if self.token_count == 0:
            return 0.0
        return round(self.average_score / self.token_count * 1000, 4)  # ×1000 for readability

    def to_dict(self) -> dict:
        return {
            "candidate_id": self.candidate_id,
            "token_count": self.token_count,
            "average_score": self.average_score,
            "quality_per_token": self.quality_per_token,
            "per_case_scores": [
                {k: getattr(s, k) for k in _WEIGHTS} | {"weighted": s.weighted}
                for s in self.per_case_scores
            ],
            "per_case_outputs": self.per_case_outputs,
        }


# ── dataset loading ────────────────────────────────────────────────────────────

def load_dataset(path: Path | None = None) -> list[TestCase]:
    if path is None:
        path = Path(__file__).parent / "dataset" / "sample_requests.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [
        TestCase(
            id=item["id"],
            source_content=item["source_content"],
            platform=item["platform"],
            expected_traits=item.get("expected_traits", []),
        )
        for item in data
    ]


# ── judge prompt ───────────────────────────────────────────────────────────────

def _judge_prompt(
    prompt_used: str,
    source_content: str,
    platform: str,
    expected_traits: list[str],
    model_output: str,
) -> str:
    traits_str = ", ".join(expected_traits) if expected_traits else "none specified"
    return f"""You are a strict social-media content quality judge.

SYSTEM PROMPT USED:
\"\"\"
{prompt_used}
\"\"\"

USER INPUT (source content):
\"\"\"
{source_content}
\"\"\"

PLATFORM: {platform}
EXPECTED TRAITS: {traits_str}

MODEL OUTPUT:
\"\"\"
{model_output}
\"\"\"

Score the output on each criterion from 0.0 to 10.0 (decimals allowed).
Consider the expected traits when scoring.

Return ONLY valid JSON with exactly these keys:
{{
  "output_quality": <float>,
  "instruction_follow": <float>,
  "relevance": <float>,
  "naturalness": <float>,
  "engagement_potential": <float>,
  "consistency": <float>,
  "reasoning": "<one sentence>"
}}"""


def _generation_prompt(prompt_template: str, source_content: str, platform: str, char_limit: int) -> str:
    """Insert test case values into a prompt template using placeholder substitution."""
    return (
        prompt_template
        .replace("{source_content}", source_content)
        .replace("{platform}", platform)
        .replace("{char_limit}", str(char_limit))
    )


# ── platform char limits (local copy to avoid importing production code) ───────

_CHAR_LIMITS = {"x": 280, "instagram": 2200, "linkedin": 3000, "facebook": 63206}


def _get_char_limit(platform: str) -> int:
    return _CHAR_LIMITS.get(platform.lower(), 2200)


# ── core evaluation ────────────────────────────────────────────────────────────

def _parse_json(raw: str) -> Any:
    cleaned = raw.strip()
    m = _JSON_FENCE_RE.search(cleaned)
    if m:
        cleaned = m.group(1).strip()
    return json.loads(cleaned)


async def _score_output(
    prompt_used: str,
    test_case: TestCase,
    model_output: str,
    llm_complete_fn,
) -> ScoreBreakdown:
    judge = _judge_prompt(prompt_used, test_case.source_content, test_case.platform, test_case.expected_traits, model_output)
    raw = await llm_complete_fn(judge, max_tokens=300)
    data = _parse_json(raw)
    return ScoreBreakdown(
        output_quality=float(data["output_quality"]),
        instruction_follow=float(data["instruction_follow"]),
        relevance=float(data["relevance"]),
        naturalness=float(data["naturalness"]),
        engagement_potential=float(data["engagement_potential"]),
        consistency=float(data["consistency"]),
    )


async def evaluate(
    prompt_key: str,
    original_text: str,
    original_tokens: int,
    candidates: list,          # list[Candidate] from compressor
    test_cases: list[TestCase],
    llm_complete_fn,
    progress_fn=None,          # optional callback(msg: str)
) -> list[CandidateResult]:
    """
    Run every candidate (+ original as baseline) against all test cases.
    Returns list of CandidateResult, sorted by quality_per_token descending.
    """
    def _log(msg: str):
        if progress_fn:
            progress_fn(msg)

    all_prompts = [
        ("original", original_text, original_tokens),
    ] + [(c.id, c.text, c.token_count) for c in candidates]

    results: list[CandidateResult] = []

    for cand_id, prompt_text, token_count in all_prompts:
        _log(f"  Evaluating candidate: {cand_id} ({token_count} tokens)...")
        result = CandidateResult(candidate_id=cand_id, token_count=token_count)

        for tc in test_cases:
            _log(f"    Test case: {tc.id} / platform: {tc.platform}")
            char_limit = _get_char_limit(tc.platform)

            # Generate output with this candidate prompt
            gen_prompt = _generation_prompt(prompt_text, tc.source_content, tc.platform, char_limit)
            try:
                model_output = await llm_complete_fn(gen_prompt, max_tokens=700)
            except Exception as e:
                model_output = f"[ERROR: {e}]"

            result.per_case_outputs.append(model_output)

            # Score it
            try:
                score = await _score_output(prompt_text, tc, model_output, llm_complete_fn)
            except Exception as e:
                _log(f"    WARNING: scoring failed for {cand_id}/{tc.id}: {e}")
                score = ScoreBreakdown(5, 5, 5, 5, 5, 5)  # neutral fallback

            result.per_case_scores.append(score)

        results.append(result)

    return results


def pick_winner(results: list[CandidateResult]) -> CandidateResult:
    """
    Select the best candidate:
    1. Never accept a candidate whose average_score < baseline - QUALITY_THRESHOLD.
    2. Among passing candidates, pick highest quality_per_token.
    """
    baseline = next((r for r in results if r.candidate_id == "original"), None)
    baseline_score = baseline.average_score if baseline else 0.0
    min_acceptable = baseline_score - QUALITY_THRESHOLD

    passing = [r for r in results if r.average_score >= min_acceptable]
    if not passing:
        return baseline  # nothing passes — fall back to original

    return max(passing, key=lambda r: r.quality_per_token)


# ── reporting ─────────────────────────────────────────────────────────────────

def format_evaluation_report(results: list[CandidateResult], winner: CandidateResult) -> str:
    baseline = next((r for r in results if r.candidate_id == "original"), None)
    baseline_score = baseline.average_score if baseline else 0.0

    lines = [
        f"{'-'*70}",
        f"  EVALUATION RESULTS",
        f"{'-'*70}",
        f"  {'Candidate':<18} {'Tokens':>8}  {'Score':>7}  {'Q/Token':>9}  {'vs Baseline':>13}  ",
        f"  {'-'*18} {'-'*8}  {'-'*7}  {'-'*9}  {'-'*13}",
    ]

    for r in sorted(results, key=lambda x: x.average_score, reverse=True):
        delta = r.average_score - baseline_score
        delta_str = f"+{delta:.2f}" if delta >= 0 else f"{delta:.2f}"
        tag = "  ← WINNER" if r.candidate_id == winner.candidate_id else ""
        lines.append(
            f"  {r.candidate_id:<18} {r.token_count:>8,}  {r.average_score:>7.2f}"
            f"  {r.quality_per_token:>9.4f}  {delta_str:>13}{tag}"
        )

    lines.append(f"{'-'*70}")
    lines.append(f"  Quality threshold: baseline − {QUALITY_THRESHOLD}  "
                 f"(min acceptable: {baseline_score - QUALITY_THRESHOLD:.2f})")
    lines.append(f"  WINNER: {winner.candidate_id}  "
                 f"(score: {winner.average_score:.2f}, tokens: {winner.token_count:,})")
    lines.append(f"{'-'*70}")
    return "\n".join(lines)
