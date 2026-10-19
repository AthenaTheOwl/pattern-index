from pathlib import Path
from datetime import date

from pattern_index.show import load_applications, rank_patterns, render


def test_render_summarizes_checked_in_corpus() -> None:
    output = render(Path("patterns"))

    assert "cross-domain pattern index" in output
    assert "15 applications" in output
    assert "5 patterns" in output
    assert "9 source repos" in output
    # the worked transfer patterns must surface in the finding line
    assert "eval-as-gate" in output
    assert "typed-artifact-discipline" in output
    assert "finding:" in output


def test_rank_orders_by_applications_then_worked() -> None:
    apps = load_applications(Path("patterns"))
    rows = rank_patterns(apps)

    assert [r.pattern_id for r in rows][:2] == [
        "eval-as-gate",
        "typed-artifact-discipline",
    ]
    # typed-artifact-discipline has the widest source-repo reach after the new mining pass
    top = rows[0]
    assert top.applications == 5
    # Relocked 2026-10-03: mcp-security-lab-DEC-MCPSEC-010 closed worked at its 90-day
    # review, taking eval-as-gate's worked count from 2 to 3.
    assert top.worked == 3


def test_render_handles_empty_corpus(tmp_path: Path) -> None:
    output = render(tmp_path)

    assert "no committed applications" in output


def test_as_of_excludes_later_applications_and_hides_later_outcomes(tmp_path: Path) -> None:
    folder = tmp_path / "example-pattern" / "applications"
    folder.mkdir(parents=True)
    for name, applied, observed in (
        ("known-later", "2026-01-01", "2026-04-01"),
        ("future-application", "2026-07-01", "2026-10-01"),
        ("undated-outcome", "2026-01-01", "null"),
    ):
        (folder / f"{name}.md").write_text(
            f"---\npattern_id: example-pattern\nsource_repo: {name}\ndec_ref: DEC-001\n"
            f"target_domain: testing\napplied_at: {applied}\noutcome: worked\n"
            f"outcome_recorded_at: {observed}\n---\n\nAn illustrative application.\n", encoding="utf-8")
    march = load_applications(tmp_path, date(2026, 3, 1))
    assert len(march) == 2 and all(a.outcome == "still-open" for a in march)
    april = load_applications(tmp_path, date(2026, 4, 1))
    assert sum(a.outcome == "worked" for a in april) == 1
    assert len(load_applications(tmp_path)) == 3
    output = render(tmp_path, date(2026, 3, 1))
    assert "as_of: 2026-03-01" in output and "0 closed reviews" in output


def test_show_cli_accepts_as_of(capsys) -> None:
    from pattern_index.cli import main

    assert main(["show", "patterns", "--as-of", "2026-03-01"]) == 0
    assert "as_of: 2026-03-01" in capsys.readouterr().out


def test_show_cli_reports_bad_as_of_as_usage_error(capsys) -> None:
    import subprocess
    import sys

    import pytest

    from pattern_index.cli import main

    with pytest.raises(SystemExit) as exc:
        main(["show", "patterns", "--as-of", "not-a-date"])
    assert exc.value.code == 2
    assert "not-a-date" in capsys.readouterr().err

    # `python -m pattern_index` from the repo root resolves the root
    # pattern_index/cli.py copy, which the in-process call above does not reach.
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "pattern_index", "show", "--as-of", "not-a-date"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "not-a-date" in result.stderr
    assert "Traceback" not in result.stderr
