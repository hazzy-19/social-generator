# Offline Prompt Optimizer

A standalone CLI tool for compressing and evaluating the social-generator AI agent's prompts. Run it **occasionally**, never during production requests.

## Goal

Find the smallest prompt that produces equal or better output quality — maximizing `quality / token_count`.

## Quick Start

```bash
# From the backend/ directory, with the virtual environment active:

# Install tiktoken for accurate token counting (one-time)
uv pip install tiktoken

# Run the full pipeline (analyze → compress → evaluate → approve)
python -m optimizer run

# Or target a specific prompt key
python -m optimizer run --prompt caption
```

## All Commands

| Command | What it does |
|---|---|
| `python -m optimizer run` | **Full pipeline** — analyze, compress, evaluate, show results, ask for approval |
| `python -m optimizer analyze` | Classify each instruction (essential / redundant / low-impact / etc.) |
| `python -m optimizer compress` | Generate 3 compressed candidates only (no LLM evaluation) |
| `python -m optimizer evaluate` | Score candidates against the test dataset |
| `python -m optimizer approve <version> <candidate>` | Approve a candidate as the active prompt |
| `python -m optimizer diff <v1> <v2>` | Show exact diff between two versions |
| `python -m optimizer history` | Show all past optimization runs |
| `python -m optimizer status` | Show current active prompt and token count |
| `python -m optimizer prompts` | List all prompt keys and their current token counts |

## Prompt Keys

| Key | Function | Notes |
|---|---|---|
| `full_extraction` | Main workhorse — image_query + hashtags + caption in one call | **Optimize this first** |
| `caption` | Standalone caption regeneration | |
| `hashtags` | Standalone hashtag regeneration | |
| `image_query` | Standalone image query extraction | |

## Compression Levels

| Level | What it does |
|---|---|
| `conservative` | Removes only redundant/low-impact instructions |
| `moderate` | Also rewrites verbose prose into tight directives |
| `aggressive` | Maximum compression; highest risk |

## Evaluation Metrics

| Metric | Weight |
|---|---|
| Output quality | 25% |
| Instruction following | 25% |
| Relevance | 15% |
| Naturalness | 15% |
| Engagement potential | 10% |
| Consistency | 10% |

**Quality always wins over brevity.** A candidate is only accepted if its score ≥ baseline − 0.3.

## File Structure

```
optimizer/
├── __init__.py
├── __main__.py         # python -m optimizer entry point
├── cli.py              # All commands
├── analyzer.py         # Instruction classification
├── compressor.py       # Candidate generation
├── evaluator.py        # Scoring and winner selection
├── token_counter.py    # tiktoken-based counting
├── store.py            # Versioned JSON persistence
├── diff.py             # Diff utilities
├── dataset/
│   └── sample_requests.json  # 6 representative test cases
└── runs/               # Created automatically
    ├── prompt_v1/
    │   ├── original.json
    │   ├── candidates.json
    │   ├── evaluation.json
    │   └── diff.json
    ├── active_prompt.json    # The approved winner
    └── history.json
```

## Using an Approved Prompt in Production

After approving a candidate, `app/ai/prompts.py` exposes an opt-in loader:

```python
from app.ai.prompts import load_active_prompt, full_extraction_prompt

# In extractor.py (opt-in):
active = load_active_prompt("full_extraction")
prompt_text = active or full_extraction_prompt(source_content, platform, char_limit)
```

The production code uses hard-coded prompts by default — switching is fully opt-in.

## Adding Your Own Test Cases

Edit `optimizer/dataset/sample_requests.json`:

```json
{
  "id": "my_tc_007",
  "platform": "instagram",
  "source_content": "Your real content here...",
  "expected_traits": ["catchy", "emojis", "hashtag-friendly"]
}
```

## Token Counter

Uses `tiktoken` with `cl100k_base` encoding (closest to DeepSeek/LLaMA family). Falls back to a word-based estimate if tiktoken is not installed. Counts are consistently comparable across candidates — that's all we need.
