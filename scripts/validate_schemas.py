from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pattern_index.validators import validate_schema


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("patterns_dir", nargs="?", default=ROOT / "patterns")
    args = parser.parse_args(argv)

    errors = validate_schema(args.patterns_dir)
    if errors:
        for error in errors:
            print(error.render())
        return 1
    print("OK schemas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
