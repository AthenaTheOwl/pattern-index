from datetime import date, timedelta

from pattern_index.model import PatternApplication


def _application(outcome: str, applied_at: date) -> PatternApplication:
    return PatternApplication.from_mapping(
        {
            "pattern_id": "eval-as-gate",
            "source_repo": "repo-a",
            "dec_ref": "DEC-001",
            "target_domain": "rag",
            "applied_at": applied_at.isoformat(),
            "outcome": outcome,
        }
    )


def test_needs_outcome_false_one_day_before_the_window() -> None:
    applied_at = date(2026, 1, 1)
    app = _application("still-open", applied_at)

    assert app.needs_outcome(applied_at + timedelta(days=89)) is False


def test_needs_outcome_true_at_ninety_days_for_open_item() -> None:
    applied_at = date(2026, 1, 1)
    app = _application("still-open", applied_at)

    assert app.needs_outcome(applied_at + timedelta(days=90)) is True


def test_needs_outcome_false_for_closed_outcome() -> None:
    applied_at = date(2026, 1, 1)
    for outcome in ("worked", "did-not-work", "abandoned"):
        app = _application(outcome, applied_at)
        assert app.needs_outcome(applied_at + timedelta(days=365)) is False
