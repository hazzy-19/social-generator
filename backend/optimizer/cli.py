"""
Offline Prompt Optimizer CLI.

Run from the backend/ directory:
    python -m optimizer <command> [options]

Commands:
    run        [--prompt KEY]   Full pipeline: analyze → compress → evaluate
    analyze    [--prompt KEY]   Classify instructions in the current prompt
    compress   [--prompt KEY]   Generate compressed candidates only
    evaluate   [--prompt KEY] [--version VN]  Evaluate candidates in a version
    approve    <version> <candidate_id> [--prompt KEY]  Approve a candidate
    diff       <version_a> <version_b> [--prompt KEY]   Show diff between versions
    history                     Show optimization history
    status                      Show current active prompt info
    prompts                     List available prompt keys

Prompt keys:  full_extraction | caption | hashtags | image_query
Default key:  full_extraction   (the main workhorse prompt)
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Make sure the backend/ package root is on the path when running as
# `python -m optimizer` from the backend/ directory.
sys.path.insert(0, str(Path(__file__).parent.parent))

# Force UTF-8 output on Windows so box-drawing chars and arrows print correctly.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from app.core.config import settings
from app.ai.client import complete as _llm_complete
from app.ai import prompts as _prompts

from optimizer import analyzer, compressor, evaluator, store, diff as _diff
from optimizer.token_counter import count_tokens, format_reduction, using_tiktoken


# ── prompt registry ────────────────────────────────────────────────────────────
# Maps a short key → a callable that returns the prompt text.
# We use a fixed representative substitution for the optimizer so token counts
# are realistic (not just an empty template).

_SAMPLE_SOURCE = (
    "We just launched QuietFlow — an AI tool that helps remote teams stay "
    "in sync without endless meetings. Early users report saving 6+ hours per week."
)
_SAMPLE_PLATFORM = "linkedin"
_SAMPLE_CHAR_LIMIT = 3000


def _get_prompt_text(key: str) -> str:
    if key == "full_extraction":
        return _prompts.full_extraction_prompt(_SAMPLE_SOURCE, _SAMPLE_PLATFORM, _SAMPLE_CHAR_LIMIT)
    elif key == "caption":
        return _prompts.caption_prompt(_SAMPLE_SOURCE, _SAMPLE_PLATFORM, _SAMPLE_CHAR_LIMIT)
    elif key == "hashtags":
        return _prompts.hashtags_prompt(_SAMPLE_SOURCE, _SAMPLE_PLATFORM)
    elif key == "image_query":
        return _prompts.image_query_prompt(_SAMPLE_SOURCE)
    else:
        raise ValueError(f"Unknown prompt key: '{key}'. Valid keys: full_extraction, caption, hashtags, image_query")


PROMPT_KEYS = ["full_extraction", "caption", "hashtags", "image_query"]
DEFAULT_PROMPT_KEY = "full_extraction"


# ── shared utilities ───────────────────────────────────────────────────────────

def _hr(char="-", width=70):
    print(char * width)


def _confirm(msg: str) -> bool:
    ans = input(f"\n{msg} [y/N] ").strip().lower()
    return ans in ("y", "yes")


def _print_token_info():
    if using_tiktoken():
        print("  Token counter: tiktoken cl100k_base")
    else:
        print("  Token counter: word-based estimate (install tiktoken for accuracy)")


# ── command implementations ────────────────────────────────────────────────────

async def cmd_prompts(_args):
    """List available prompt keys and their current token counts."""
    _hr()
    print("  AVAILABLE PROMPT KEYS")
    _hr()
    _print_token_info()
    print()
    for key in PROMPT_KEYS:
        try:
            text = _get_prompt_text(key)
            tokens = count_tokens(text)
            active = store.active_prompt_status().get(key)
            active_str = f"  [ACTIVE: {active['candidate_id']} / {active['token_count']} tokens]" if active else ""
            print(f"  {key:<20} {tokens:>6} tokens{active_str}")
        except Exception as e:
            print(f"  {key:<20}  ERROR: {e}")
    _hr()


async def cmd_status(_args):
    """Show the current active prompt configuration."""
    active = store.active_prompt_status()
    _hr()
    print("  ACTIVE PROMPT STATUS")
    _hr()
    _print_token_info()
    print()
    if not active:
        print("  No prompts approved yet. Run 'python -m optimizer run' first.")
    else:
        for key, info in active.items():
            print(f"  Prompt   : {key}")
            print(f"  Version  : {info['version']}")
            print(f"  Candidate: {info['candidate_id']}")
            print(f"  Tokens   : {info['token_count']:,}")
            print(f"  Approved : {info['approved_at']}")
            print()
    _hr()


async def cmd_history(_args):
    """Show the optimization run history."""
    history = store.load_history()
    _hr()
    print("  OPTIMIZATION HISTORY")
    _hr()
    if not history:
        print("  No history yet.")
    for i, entry in enumerate(reversed(history)):
        event = entry.get("event", "?")
        at = entry.get("at", "?")
        if event == "run":
            v = entry.get("version", "?")
            keys = ", ".join(entry.get("prompt_keys", []))
            print(f"  [{at}]  RUN   version={v}  prompts={keys}")
        elif event == "approved":
            v = entry.get("version", "?")
            cid = entry.get("candidate_id", "?")
            pk = entry.get("prompt_key", "?")
            print(f"  [{at}]  APPROVED  {pk} → {v}/{cid}")
    _hr()


async def cmd_diff(args):
    """Show diff between two versions."""
    version_a = args.version_a
    version_b = args.version_b
    key = args.prompt or DEFAULT_PROMPT_KEY

    data_a = store.load_version(version_a)
    data_b = store.load_version(version_b)

    orig_a = data_a["original"].get(key)
    # For version_b, the "optimized" text might be a candidate
    cands_b = data_b["candidates"].get(key, [])

    if not orig_a:
        print(f"ERROR: No original found for prompt '{key}' in {version_a}")
        return

    # Show diffs between version_a original and each candidate in version_b
    for cand in cands_b:
        report = _diff.format_diff_report(
            version_a=f"{version_a}/original",
            version_b=f"{version_b}/{cand['id']}",
            prompt_key=key,
            original=orig_a["text"],
            optimized=cand["text"],
            original_tokens=orig_a["token_count"],
            optimized_tokens=cand["token_count"],
        )
        print(report)
        print()


async def cmd_approve(args):
    """Approve a specific candidate as the active prompt."""
    version = args.version
    candidate_id = args.candidate_id
    key = args.prompt or DEFAULT_PROMPT_KEY

    # Show a summary before confirming
    version_data = store.load_version(version)
    orig = version_data["original"].get(key)
    cands = version_data["candidates"].get(key, [])
    cand = next((c for c in cands if c["id"] == candidate_id), None)

    if cand is None:
        print(f"ERROR: Candidate '{candidate_id}' not found in {version}/{key}")
        print(f"Available: {[c['id'] for c in cands]}")
        return

    _hr()
    print(f"  Approving:  {version} / {key} / {candidate_id}")
    if orig:
        print(f"  Original tokens : {orig['token_count']:,}")
    print(f"  Candidate tokens: {cand['token_count']:,}")
    if orig:
        print(f"  Reduction       : {format_reduction(orig['token_count'], cand['token_count'])}")
    _hr()
    print()
    print("  CANDIDATE PROMPT:")
    print()
    print(cand["text"])
    print()

    if not _confirm(f"Approve this candidate as the active '{key}' prompt?"):
        print("  Aborted.")
        return

    record = store.approve(version, key, candidate_id)
    print(f"\n  ✓ Approved and saved to active_prompt.json")
    print(f"  Production code can now call store.load_active_prompts() to use it.")


async def cmd_analyze(args):
    """Analyze the current prompt and classify its instructions."""
    key = args.prompt or DEFAULT_PROMPT_KEY
    prompt_text = _get_prompt_text(key)
    tokens = count_tokens(prompt_text)

    print(f"\n  Analyzing prompt: {key}  ({tokens:,} tokens)  ...")
    instructions = await analyzer.analyze(prompt_text, _llm_complete)
    report = analyzer.format_analysis_report(instructions)
    print(report)
    return instructions


async def cmd_compress(args):
    """Analyze and generate compressed candidates (does not evaluate)."""
    key = args.prompt or DEFAULT_PROMPT_KEY
    prompt_text = _get_prompt_text(key)
    original_tokens = count_tokens(prompt_text)

    print(f"\n  Analyzing prompt: {key}  ({original_tokens:,} tokens)  ...")
    instructions = await analyzer.analyze(prompt_text, _llm_complete)
    print(analyzer.format_analysis_report(instructions))

    print(f"\n  Compressing at 3 levels  ...")
    candidates = await compressor.compress(key, prompt_text, instructions, _llm_complete)
    print(compressor.format_candidates_report(key, original_tokens, candidates))

    return candidates


async def cmd_evaluate(args):
    """Evaluate existing candidates for a version (or re-run compression first)."""
    key = args.prompt or DEFAULT_PROMPT_KEY
    version = args.version

    if version:
        vdata = store.load_version(version)
        cands_raw = vdata["candidates"].get(key, [])
        if not cands_raw:
            print(f"ERROR: No candidates found for '{key}' in version {version}.")
            return
        from optimizer.compressor import Candidate
        cands = [Candidate(id=c["id"], level=c["level"], text=c["text"], token_count=c["token_count"]) for c in cands_raw]
        orig_data = vdata["original"].get(key, {})
        prompt_text = orig_data.get("text", _get_prompt_text(key))
        original_tokens = orig_data.get("token_count", count_tokens(prompt_text))
    else:
        print("  --version not specified; running compress first...")
        prompt_text = _get_prompt_text(key)
        original_tokens = count_tokens(prompt_text)
        instructions = await analyzer.analyze(prompt_text, _llm_complete)
        cands = await compressor.compress(key, prompt_text, instructions, _llm_complete)

    dataset = evaluator.load_dataset()
    print(f"\n  Evaluating {len(cands) + 1} candidates against {len(dataset)} test cases  ...")
    print("  (This makes multiple LLM calls — may take a minute)\n")

    results = await evaluator.evaluate(
        prompt_key=key,
        original_text=prompt_text,
        original_tokens=original_tokens,
        candidates=cands,
        test_cases=dataset,
        llm_complete_fn=_llm_complete,
        progress_fn=lambda msg: print(msg),
    )

    winner = evaluator.pick_winner(results)
    print(evaluator.format_evaluation_report(results, winner))
    return results, winner


async def cmd_run(args):
    """
    Full pipeline: analyze → compress → evaluate → show results → ask to approve.
    This is the main command you'll run occasionally.
    """
    key = args.prompt or DEFAULT_PROMPT_KEY
    prompt_text = _get_prompt_text(key)
    original_tokens = count_tokens(prompt_text)
    version = store.next_version_name()

    _hr("═")
    print(f"  PROMPT OPTIMIZER  —  {key}")
    _print_token_info()
    print(f"  Version       : {version}")
    print(f"  Original tokens: {original_tokens:,}")
    _hr("═")

    # 1. Save original
    store.save_original(version, key, prompt_text, original_tokens)

    # 2. Analyze
    print(f"\n  [1/3]  Analyzing instructions  ...")
    instructions = await analyzer.analyze(prompt_text, _llm_complete)
    print(analyzer.format_analysis_report(instructions))

    # 3. Compress
    print(f"\n  [2/3]  Generating compressed candidates  ...")
    candidates = await compressor.compress(key, prompt_text, instructions, _llm_complete)
    print(compressor.format_candidates_report(key, original_tokens, candidates))
    store.save_candidates(version, key, [c.to_dict() for c in candidates])

    # Save diffs
    for c in candidates:
        diff_data = _diff.side_by_side_summary(prompt_text, c.text)
        store.save_diff(version, key, {c.id: diff_data})

    # 4. Evaluate
    print(f"\n  [3/3]  Evaluating all candidates  ...")
    print("  (This makes multiple LLM calls — may take a minute)\n")
    dataset = evaluator.load_dataset()
    results = await evaluator.evaluate(
        prompt_key=key,
        original_text=prompt_text,
        original_tokens=original_tokens,
        candidates=candidates,
        test_cases=dataset,
        llm_complete_fn=_llm_complete,
        progress_fn=lambda msg: print(msg),
    )
    winner = evaluator.pick_winner(results)

    # Save evaluation
    store.save_evaluation(version, key, [r.to_dict() for r in results])
    store.append_run_history(version, [key], {"winner": winner.candidate_id, "winner_score": winner.average_score})

    # 5. Print final report
    _hr("═")
    print(evaluator.format_evaluation_report(results, winner))
    _hr("═")

    if winner.candidate_id == "original":
        print("\n  The original prompt is already optimal. No approval needed.")
        return

    # Print the winning candidate
    winning_cand = next((c for c in candidates if c.id == winner.candidate_id), None)
    if winning_cand:
        print(f"\n  WINNING CANDIDATE  ({winner.candidate_id}):")
        print()
        print(winning_cand.text)
        print()
        print(f"  Original : {original_tokens:,} tokens")
        print(f"  Optimized: {winner.token_count:,} tokens  "
              f"({format_reduction(original_tokens, winner.token_count)})")
        print(f"  Quality  : original {results[0].average_score:.2f} → "
              f"winner {winner.average_score:.2f}")
        print()

        # Human approval
        if _confirm(f"Approve '{winner.candidate_id}' as the active '{key}' prompt?"):
            store.approve(version, key, winner.candidate_id)
            print(f"\n  ✓ Approved! Active prompt saved.")
            print(f"  To use it in production, call store.load_active_prompts() in prompts.py.")
        else:
            print(f"\n  Not approved. Results saved to optimizer/runs/{version}/")
            print(f"  You can approve later with:")
            print(f"    python -m optimizer approve {version} {winner.candidate_id} --prompt {key}")


# ── CLI entry point ────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m optimizer",
        description="Offline Prompt Optimizer for the social-generator AI agent.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # run
    r = sub.add_parser("run", help="Full pipeline: analyze → compress → evaluate")
    r.add_argument("--prompt", choices=PROMPT_KEYS, default=DEFAULT_PROMPT_KEY,
                   help=f"Prompt key to optimize (default: {DEFAULT_PROMPT_KEY})")

    # analyze
    a = sub.add_parser("analyze", help="Classify instructions in the current prompt")
    a.add_argument("--prompt", choices=PROMPT_KEYS, default=DEFAULT_PROMPT_KEY)

    # compress
    cmp = sub.add_parser("compress", help="Generate compressed candidates (no evaluation)")
    cmp.add_argument("--prompt", choices=PROMPT_KEYS, default=DEFAULT_PROMPT_KEY)

    # evaluate
    ev = sub.add_parser("evaluate", help="Evaluate candidates for a version")
    ev.add_argument("--prompt", choices=PROMPT_KEYS, default=DEFAULT_PROMPT_KEY)
    ev.add_argument("--version", help="Version name, e.g. prompt_v1 (omit to re-compress first)")

    # approve
    ap = sub.add_parser("approve", help="Approve a candidate as the active prompt")
    ap.add_argument("version", help="Version name, e.g. prompt_v1")
    ap.add_argument("candidate_id", help="Candidate ID: conservative | moderate | aggressive")
    ap.add_argument("--prompt", choices=PROMPT_KEYS, default=DEFAULT_PROMPT_KEY)

    # diff
    df = sub.add_parser("diff", help="Show diff between two versions")
    df.add_argument("version_a", help="First version, e.g. prompt_v1")
    df.add_argument("version_b", help="Second version, e.g. prompt_v2")
    df.add_argument("--prompt", choices=PROMPT_KEYS, default=DEFAULT_PROMPT_KEY)

    # history
    sub.add_parser("history", help="Show optimization history")

    # status
    sub.add_parser("status", help="Show current active prompt info")

    # prompts
    sub.add_parser("prompts", help="List available prompt keys and token counts")

    return p


_COMMAND_MAP = {
    "run":      cmd_run,
    "analyze":  cmd_analyze,
    "compress": cmd_compress,
    "evaluate": cmd_evaluate,
    "approve":  cmd_approve,
    "diff":     cmd_diff,
    "history":  cmd_history,
    "status":   cmd_status,
    "prompts":  cmd_prompts,
}


async def _main():
    parser = build_parser()
    args = parser.parse_args()
    fn = _COMMAND_MAP[args.command]
    await fn(args)


if __name__ == "__main__":
    asyncio.run(_main())
