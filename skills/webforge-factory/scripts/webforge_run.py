#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run WEBFORGE factory CLI from the bundled skill.")
    parser.add_argument("webforge_args", nargs=argparse.REMAINDER, help="Arguments passed to python3 -m webforge.")
    args = parser.parse_args(argv)
    repo_root = repo_root_from_script()
    sys.path.insert(0, str(repo_root))
    from webforge.cli import main as webforge_main

    forwarded = args.webforge_args or ["doctor", "--project-root", str(repo_root)]
    return webforge_main(forwarded)


if __name__ == "__main__":
    raise SystemExit(main())
