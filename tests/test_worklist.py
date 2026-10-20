from __future__ import annotations

from datetime import date
from pathlib import Path

from pattern_index.frontmatter import dump_frontmatter
from pattern_index.worklist import outcome_worklist, render_worklist


def write_application(root: Path, pattern_id: str, applied_at: str, outcome: str = "still-open") -> Path:
    path = root / pattern_id / "applications" / f"{pattern_id}-{applied_at}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "pattern_id": pattern_id,
        "source_repo": "fixture-repo",
        "dec_ref": "DEC-FIX-001",
        "target_domain": "fixture-domain",
        "applied_at": applied_at,
        "outcome": outcome,
        "outcome_recorded_at": None,
        "outcome_evidence": ["Still open; fixture for worklist."],
    }
    path.write_text(dump_frontmatter(metadata, "## Narrative\n\nFixture."), encoding="utf-8")
    return path


def test_outcome_worklist_returns_due_and_upcoming_items(tmp_path: Path) -> None:
    write_application(tmp_path, "eval-as-gate", "2026-04-01")
    write_application(tmp_path, "typed-artifact-discipline", "2026-06-15")

    items = outcome_worklist(tmp_path, as_of=date(2026, 7, 5), horizon_days=30)

    assert [item.pattern_id for item in items] == ["eval-as-gate"]
    assert items[0].days_until_due == -5


def test_outcome_worklist_ignores_closed_items(tmp_path: Path) -> None:
    write_application(tmp_path, "eval-as-gate", "2026-04-01", outcome="worked")

    assert outcome_worklist(tmp_path, as_of=date(2026, 7, 5), horizon_days=30) == []


def test_render_worklist_includes_dec_reference(tmp_path: Path) -> None:
    write_application(tmp_path, "eval-as-gate", "2026-04-01")

    output = render_worklist(tmp_path, as_of=date(2026, 7, 5), horizon_days=30)

    assert "90-day outcome worklist" in output
    assert "DEC-FIX-001" in output
    assert "eval-as-gate" in output

def test_worklist_cli_reports_bad_as_of_as_usage_error(tmp_path: Path, capsys) -> None:
    import pytest

    from pattern_index.cli import main

    with pytest.raises(SystemExit) as exc:
        main(["worklist", str(tmp_path), "--as-of", "nope"])
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "pattern-index worklist" in err and "--as-of" in err and "nope" in err


def test_worklist_cli_accepts_as_of(tmp_path: Path, capsys) -> None:
    from pattern_index.cli import main

    write_application(tmp_path, "eval-as-gate", "2026-04-01")

    assert main(["worklist", str(tmp_path), "--as-of", "2026-07-05"]) == 0
    assert "as_of: 2026-07-05" in capsys.readouterr().out
