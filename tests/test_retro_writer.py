from pathlib import Path

from pattern_index.retro.writer import build_retro


def test_build_retro_counts_checked_in_corpus() -> None:
    retro = build_retro("2026-Q2", Path("patterns"))

    assert "Applications reviewed: 10" in retro
    assert "- eval-as-gate: 2" in retro
    assert "- still-open: 6" in retro
    assert "- worked: 2" in retro
