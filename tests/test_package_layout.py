import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PACKAGE = ROOT / "src" / "pattern_index"


def test_no_module_exists_only_in_the_root_shim() -> None:
    # The wheel packages src/pattern_index alone, so a module that lives only
    # under the root pattern_index/ directory is missing from an installed copy.
    root_modules = {path.name for path in (ROOT / "pattern_index").glob("*.py")}
    src_modules = {path.name for path in SRC_PACKAGE.glob("*.py")}
    assert root_modules <= src_modules


def test_repo_root_imports_resolve_to_src() -> None:
    # `python -m pattern_index` from a checkout imports the root pattern_index/
    # directory first; every submodule must still come from src/pattern_index.
    env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONSAFEPATH"}}
    code = (
        "import importlib\n"
        "for name in ('__main__', 'cli', 'model', 'scoring'):\n"
        "    print(importlib.import_module('pattern_index.' + name).__file__)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    files = [Path(line).resolve() for line in result.stdout.splitlines()]
    assert len(files) == 4
    assert all(path.parent == SRC_PACKAGE for path in files), files
