"""Typed model for checked-in pattern application records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from pattern_index.frontmatter import read_markdown


@dataclass(frozen=True)
class PatternApplication:
    pattern_id: str
    source_repo: str
    dec_ref: str
    target_domain: str
    applied_at: date
    outcome: str
    outcome_recorded_at: date | None
    outcome_evidence: tuple[str, ...]
    path: Path | None = None

    @classmethod
    def from_file(cls, path: str | Path) -> "PatternApplication":
        source_path = Path(path)
        metadata, _body = read_markdown(source_path)
        return cls.from_mapping(metadata, path=source_path)

    @classmethod
    def from_mapping(
        cls,
        metadata: dict[str, Any],
        path: str | Path | None = None,
    ) -> "PatternApplication":
        evidence = metadata.get("outcome_evidence") or ()
        if isinstance(evidence, str):
            evidence = (evidence,)

        return cls(
            pattern_id=str(metadata["pattern_id"]),
            source_repo=str(metadata["source_repo"]),
            dec_ref=str(metadata["dec_ref"]),
            target_domain=str(metadata["target_domain"]),
            applied_at=date.fromisoformat(str(metadata["applied_at"])),
            outcome=str(metadata["outcome"]),
            outcome_recorded_at=_parse_optional_date(metadata.get("outcome_recorded_at")),
            outcome_evidence=tuple(str(item) for item in evidence),
            path=Path(path) if path is not None else None,
        )

    def needs_outcome(self, as_of: date) -> bool:
        age_days = (as_of - self.applied_at).days
        return age_days >= 90 and self.outcome == "still-open"


def _parse_optional_date(value: object) -> date | None:
    if value in {None, ""}:
        return None
    return date.fromisoformat(str(value))
