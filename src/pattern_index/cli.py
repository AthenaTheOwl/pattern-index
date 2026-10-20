"""Command line interface for Pattern Index."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

from pattern_index.mine import mine_repo
from pattern_index.retro import write_retro
from pattern_index.show import CorpusDataError
from pattern_index.show import render as render_show
from pattern_index.validators import (
    validate_outcomes,
    validate_record_dates,
    validate_schema,
)
from pattern_index.worklist import render_worklist


def _default_patterns_dir() -> Path:
    """The bundled patterns/ corpus at the repo root.

    Lets `python -m pattern_index validate` run with no positional arg
    against the committed corpus.
    """
    return Path(__file__).resolve().parents[2] / "patterns"


def _iso_date(value: str) -> date:
    """argparse type for --as-of: a calendar date written exactly YYYY-MM-DD.

    date.fromisoformat alone also accepts forms such as 20260630 and
    2026-W26, which the help text does not promise.
    """
    if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        try:
            return date.fromisoformat(value)
        except ValueError:
            pass
    raise argparse.ArgumentTypeError(f"expected a YYYY-MM-DD date, got {value!r}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pattern-index")
    subparsers = parser.add_subparsers(dest="command", required=True)

    mine = subparsers.add_parser("mine", help="mine DEC record fields for cross-domain candidates")
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
    validate.add_argument(
        "--repos-root",
        type=Path,
        default=None,
        help="Directory holding source repo checkouts, for the applied_at date check. "
        "Defaults to the parent of the repo that holds the patterns dir.",
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
    show.add_argument(
        "--as-of",
        type=_iso_date,
        help="Exclude later applications and outcome observations (YYYY-MM-DD).",
    )

    worklist = subparsers.add_parser(
        "worklist", help="list still-open applications due for 90-day review"
    )
    worklist.add_argument(
        "patterns_dir",
        type=Path,
        nargs="?",
        default=None,
        help="Patterns dir to inspect. Defaults to the bundled patterns/ corpus.",
    )
    worklist.add_argument(
        "--as-of", type=_iso_date, help="Review date as YYYY-MM-DD. Defaults to today."
    )
    worklist.add_argument(
        "--horizon-days",
        type=int,
        default=30,
        help="Include reviews due within this many days. Defaults to 30.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "mine":
        written = mine_repo(args.repo, args.out, args.primary_domain)
        for path in written:
            print(f"WROTE {path}")
        if not written:
            print("No cross-domain DEC candidates found.")
        return 0

    if args.command == "validate":
        patterns_dir = args.patterns_dir or _default_patterns_dir()
        repos_root = args.repos_root or Path(patterns_dir).resolve().parent.parent
        date_errors, seed_warnings = validate_record_dates(patterns_dir, repos_root)
        for warning in seed_warnings:
            print(f"WARN (seed-illustrative) {warning.render()}")
        errors = validate_schema(patterns_dir) + validate_outcomes(patterns_dir) + date_errors
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
        try:
            output = render_show(args.patterns_dir, args.as_of)
        except CorpusDataError as err:
            # A data problem in the corpus, not a usage mistake: no usage line, exit 1.
            print(f"pattern-index show: error: {err}", file=sys.stderr)
            return 1
        print(output, end="")
        return 0

    if args.command == "worklist":
        patterns_dir = args.patterns_dir or _default_patterns_dir()
        print(render_worklist(patterns_dir, args.as_of, args.horizon_days), end="")
        return 0

    return 1
