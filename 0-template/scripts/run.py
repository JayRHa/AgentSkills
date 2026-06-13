#!/usr/bin/env python3
"""Example helper script for a skill.

Skills can bundle runnable scripts that the agent executes when useful.
Keep them dependency-free (standard library) where possible, parse arguments,
and print clear output.

Usage:
    python3 run.py --name World
"""
import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Example skill helper.")
    parser.add_argument("--name", default="World", help="Name to greet.")
    args = parser.parse_args()
    print(f"Hello, {args.name}! Replace this with real skill logic.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
