from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pattern_index.validators import lint_voice


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", default=[ROOT / "patterns"])
    args = parser.parse_args(argv)

    errors = lint_voice(args.paths)
    if errors:
        for error in errors:
            print(error.render())
        return 1
    print("OK voice")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
