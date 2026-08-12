#!/usr/bin/env python3
"""
Startup / run entry point for the Image Compressor & Converter Skill.

Thin wrapper around `image_compressor.py` so the skill can be started with
`python run.py` and accepts the exact same CLI arguments.

Built and generated using IronClaw AI Agent.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure we can import the sibling CLI module regardless of CWD.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from image_compressor import main  # noqa: E402


def run() -> int:
    """Delegate to the CLI's main() and map it to an exit code."""
    try:
        return main(sys.argv[1:])
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(run())