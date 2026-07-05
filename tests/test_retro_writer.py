from pathlib import Path

from pattern_index.retro.writer import build_retro


def test_build_retro_counts_checked_in_corpus() -> None:
    retro = build_retro("2026-Q2", Path("patterns"))

    assert "Applications reviewed: 13" in retro
    assert "- eval-as-gate: 3" in retro
    assert "- still-open: 8" in retro
    assert "- worked: 3" in retro
