from pathlib import Path

from pattern_index.show import load_applications, rank_patterns, render


def test_render_summarizes_checked_in_corpus() -> None:
    output = render(Path("patterns"))

    assert "cross-domain pattern index" in output
    assert "10 applications" in output
    assert "5 patterns" in output
    assert "6 source repos" in output
    # the two worked transfers must surface in the finding line
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
    # eval-as-gate has one worked outcome out of two applications
    top = rows[0]
    assert top.applications == 2
    assert top.worked == 1


def test_render_handles_empty_corpus(tmp_path: Path) -> None:
    output = render(tmp_path)

    assert "no committed applications" in output
