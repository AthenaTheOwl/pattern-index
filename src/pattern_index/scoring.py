"""Summary scoring helpers for report artifacts and tests."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pattern_index.model import PatternApplication
from pattern_index.validators import iter_application_files


@dataclass(frozen=True)
class PatternScorecard:
    applications_reviewed: int
    source_repos_represented: int
    pattern_counts: dict[str, int]
    outcome_counts: dict[str, int]


def score_patterns(patterns_dir: str | Path) -> PatternScorecard:
    applications = [
        PatternApplication.from_file(path)
        for path in iter_application_files(Path(patterns_dir))
    ]
    return score_applications(applications)


def score_applications(
    applications: Iterable[PatternApplication],
) -> PatternScorecard:
    collected = list(applications)
    return PatternScorecard(
        applications_reviewed=len(collected),
        source_repos_represented=len({item.source_repo for item in collected}),
        pattern_counts=dict(Counter(item.pattern_id for item in collected)),
        outcome_counts=dict(Counter(item.outcome for item in collected)),
    )
