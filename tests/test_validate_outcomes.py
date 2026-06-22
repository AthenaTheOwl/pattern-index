from datetime import date
from pathlib import Path

from pattern_index.frontmatter import dump_frontmatter
from pattern_index.validators import validate_outcomes, validate_schema


def write_application(
    root: Path,
    *,
    pattern_id: str = "eval-as-gate",
    applied_at: str = "2026-01-01",
    outcome: str = "still-open",
    recorded_at: str | None = None,
) -> Path:
    taxonomy = root / "_taxonomy.yaml"
    taxonomy.write_text("pattern_ids:\n  - eval-as-gate\n", encoding="utf-8")

    target = root / pattern_id / "applications" / "fixture-DEC-001.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        dump_frontmatter(
            {
                "pattern_id": pattern_id,
                "source_repo": "fixture",
                "dec_ref": "DEC-001",
                "target_domain": "rag-eval-discipline",
                "applied_at": applied_at,
                "outcome": outcome,
                "outcome_recorded_at": recorded_at,
                "outcome_evidence": ["Worked; fixture evidence."],
            },
            "## Narrative\n\nFixture entry.",
        ),
        encoding="utf-8",
    )
    return target


def test_validate_schema_accepts_valid_application(tmp_path: Path) -> None:
    write_application(
        tmp_path,
        applied_at="2026-02-01",
        outcome="worked",
        recorded_at="2026-06-01",
    )

    assert validate_schema(tmp_path) == []


def test_validate_outcomes_rejects_old_still_open(tmp_path: Path) -> None:
    write_application(tmp_path, applied_at="2026-01-01", outcome="still-open")

    errors = validate_outcomes(tmp_path, as_of=date(2026, 6, 21))

    assert [error.message for error in errors] == [
        "still-open outcome is older than 90 days"
    ]


def test_validate_outcomes_allows_recent_still_open(tmp_path: Path) -> None:
    write_application(tmp_path, applied_at="2026-05-01", outcome="still-open")

    assert validate_outcomes(tmp_path, as_of=date(2026, 6, 21)) == []
