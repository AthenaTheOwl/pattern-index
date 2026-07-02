from pathlib import Path

from pattern_index.model import PatternApplication
from pattern_index.scoring import score_applications, score_patterns


def test_score_patterns_locks_checked_in_corpus() -> None:
    scorecard = score_patterns(Path("patterns"))

    assert scorecard.applications_reviewed == 10
    assert scorecard.source_repos_represented == 6
    assert scorecard.pattern_counts == {
        "citation-faithful-extraction": 2,
        "dec-then-implement": 2,
        "eval-as-gate": 2,
        "typed-artifact-discipline": 2,
        "voice-lint-as-spec-check": 2,
    }
    assert scorecard.outcome_counts == {
        "abandoned": 1,
        "did-not-work": 1,
        "still-open": 6,
        "worked": 2,
    }


def test_score_applications_counts_each_field() -> None:
    apps = [
        PatternApplication.from_mapping(
            {
                "pattern_id": "eval-as-gate",
                "source_repo": "repo-a",
                "dec_ref": "DEC-001",
                "target_domain": "rag",
                "applied_at": "2026-01-01",
                "outcome": "worked",
            }
        ),
        PatternApplication.from_mapping(
            {
                "pattern_id": "eval-as-gate",
                "source_repo": "repo-b",
                "dec_ref": "DEC-002",
                "target_domain": "rag",
                "applied_at": "2026-01-02",
                "outcome": "still-open",
            }
        ),
        PatternApplication.from_mapping(
            {
                "pattern_id": "typed-artifact-discipline",
                "source_repo": "repo-a",
                "dec_ref": "DEC-003",
                "target_domain": "eval",
                "applied_at": "2026-01-03",
                "outcome": "worked",
            }
        ),
    ]

    scorecard = score_applications(apps)

    assert scorecard.applications_reviewed == 3
    assert scorecard.source_repos_represented == 2
    assert scorecard.pattern_counts == {
        "eval-as-gate": 2,
        "typed-artifact-discipline": 1,
    }
    assert scorecard.outcome_counts == {"worked": 2, "still-open": 1}
