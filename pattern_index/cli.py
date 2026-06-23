"""Command line entrypoint kept at the factory-declared module path."""

from __future__ import annotations

import argparse
from pathlib import Path

from pattern_index.mine import mine_repo
from pattern_index.retro import write_retro
from pattern_index.show import render as render_show
from pattern_index.validators import validate_outcomes, validate_schema


def _default_patterns_dir() -> Path:
    """The bundled patterns/ corpus at the repo root.

    Lets `python -m pattern_index validate` run with no positional arg
    against the committed corpus.
    """
    return Path(__file__).resolve().parents[1] / "patterns"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pattern-index")
    subparsers = parser.add_subparsers(dest="command", required=True)

    mine = subparsers.add_parser("mine", help="mine DEC frontmatter")
    mine.add_argument("--repo", required=True, type=Path)
    mine.add_argument("--out", required=True, type=Path)
    mine.add_argument("--primary-domain")

    validate = subparsers.add_parser("validate", help="validate patterns corpus")
    validate.add_argument(
        "patterns_dir",
        type=Path,
        nargs="?",
        default=None,
        help="Patterns dir to validate. Defaults to the bundled patterns/ corpus.",
    )

    retro = subparsers.add_parser("retro", help="write quarterly retro")
    retro.add_argument("--quarter", required=True)
    retro.add_argument("--out", required=True, type=Path)
    retro.add_argument("--patterns-dir", type=Path)

    show = subparsers.add_parser(
        "show", help="print a ranked summary of the committed patterns corpus"
    )
    show.add_argument(
        "patterns_dir",
        type=Path,
        nargs="?",
        default=None,
        help="Patterns dir to summarize. Defaults to the bundled patterns/ corpus.",
    )

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
        patterns_dir = args.patterns_dir or _default_patterns_dir()
        errors = validate_schema(patterns_dir) + validate_outcomes(patterns_dir)
        if errors:
            for error in errors:
                print(error.render())
            return 1
        print(f"OK {patterns_dir}")
        return 0

    if args.command == "retro":
        out_path = write_retro(args.quarter, args.out, args.patterns_dir)
        print(f"WROTE {out_path}")
        return 0

    if args.command == "show":
        print(render_show(args.patterns_dir), end="")
        return 0

    return 1
