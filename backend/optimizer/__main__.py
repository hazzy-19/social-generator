"""
Enables: python -m optimizer <command>
"""
from optimizer.cli import _main
import asyncio

asyncio.run(_main())
