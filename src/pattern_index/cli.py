"""Command line interface for Pattern Index."""

from __future__ import annotations

import argparse
from pathlib import Path

from pattern_index.mine import mine_repo
from pattern_index.retro import write_retro
from pattern_index.validators import validate_outcomes, validate_schema


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pattern-index")
    subparsers = parser.add_subparsers(dest="command", required=True)

    mine = subparsers.add_parser("mine", help="mine DEC frontmatter")
    mine.add_argument("--repo", required=True, type=Path)
    mine.add_argument("--out", required=True, type=Path)
    mine.add_argument("--primary-domain")

    validate = subparsers.add_parser("validate", help="validate patterns corpus")
    validate.add_argument("patterns_dir", type=Path)

    retro = subparsers.add_parser("retro", help="write quarterly retro")
    retro.add_argument("--quarter", required=True)
    retro.add_argument("--out", required=True, type=Path)
    retro.add_argument("--patterns-dir", type=Path)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "mine":
        written = mine_repo(args.repo, args.out, args.primary_domain)
        for path in written:
            print(f"WROTE {path}")
        if not written:
            print("No cross-domain DEC candidates found.")
        return 0

    if args.command == "validate":
        errors = validate_schema(args.patterns_dir) + validate_outcomes(args.patterns_dir)
        if errors:
            for error in errors:
                print(error.render())
            return 1
        print(f"OK {args.patterns_dir}")
        return 0

    if args.command == "retro":
        out_path = write_retro(args.quarter, args.out, args.patterns_dir)
        print(f"WROTE {out_path}")
        return 0

    return 1
