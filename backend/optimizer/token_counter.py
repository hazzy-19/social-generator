"""
Accurate token counting using tiktoken.

Uses cl100k_base encoding — the closest publicly available tokenizer to
DeepSeek/LLaMA-family models. Actual token counts may differ slightly but
are consistently comparable across versions, which is all we need for
relative measurement.

Falls back to a word-based estimate if tiktoken is not installed.
"""
from __future__ import annotations

_encoder = None


def _get_encoder():
    global _encoder
    if _encoder is not None:
        return _encoder
    try:
        import tiktoken
        _encoder = tiktoken.get_encoding("cl100k_base")
    except ImportError:
        _encoder = None
    return _encoder


def count_tokens(text: str) -> int:
    """Return the token count for *text*."""
    enc = _get_encoder()
    if enc is not None:
        return len(enc.encode(text))
    # Fallback: rough word-based estimate (1 word ≈ 1.3 tokens)
    return int(len(text.split()) * 1.3)


def using_tiktoken() -> bool:
    return _get_encoder() is not None


def format_reduction(original: int, optimized: int) -> str:
    """Return a human-readable reduction string, e.g. '↓ 42.9%'."""
    if original == 0:
        return "n/a"
    pct = (original - optimized) / original * 100
    arrow = "↓" if pct > 0 else "↑"
    return f"{arrow} {abs(pct):.1f}%"
