"""Command-line entry point for the I language."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .interpreter import run_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="i", description="Run I language programs.")
    parser.add_argument("path", nargs="?", help="Path to a .i source file")
    parser.add_argument("--version", action="store_true", help="Show the I version and exit")
    args = parser.parse_args(argv)

    if args.version:
        print(f"I {__version__}")
        return 0

    if not args.path:
        parser.print_help()
        return 1

    run_file(args.path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
