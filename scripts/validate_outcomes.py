from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pattern_index.validators import validate_outcomes, validate_record_dates  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("patterns_dir", nargs="?", default=ROOT / "patterns")
    parser.add_argument(
        "--repos-root",
        type=Path,
        default=None,
        help="Directory holding source repo checkouts. Defaults to this repo's parent.",
    )
    args = parser.parse_args(argv)

    repos_root = args.repos_root or Path(args.patterns_dir).resolve().parent.parent
    date_errors, seed_warnings = validate_record_dates(args.patterns_dir, repos_root)
    for warning in seed_warnings:
        print(f"WARN (seed-illustrative) {warning.render()}")
    errors = validate_outcomes(args.patterns_dir) + date_errors
    if errors:
        for error in errors:
            print(error.render())
        return 1
    print("OK outcomes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
