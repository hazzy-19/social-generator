"""
Offline Prompt Optimizer for the social-generator AI agent.

This package is a standalone CLI tool — it is NEVER imported by the
production FastAPI application. Run it occasionally to compress and
evaluate your master prompts, then approve the best candidate.

Usage:
    cd backend
    python -m optimizer run          # full pipeline
    python -m optimizer status       # show active prompt info
    python -m optimizer --help       # all commands
"""
