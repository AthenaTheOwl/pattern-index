"""Outcome-review worklist for still-open pattern applications."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from pattern_index.frontmatter import read_markdown
from pattern_index.validators import iter_application_files, parse_date

REVIEW_WINDOW_DAYS = 90


@dataclass(frozen=True)
class WorklistItem:
    pattern_id: str
    source_repo: str
    dec_ref: str
    applied_at: date
    due_at: date
    days_until_due: int
    path: Path


def outcome_worklist(
    patterns_dir: str | Path,
    as_of: date | None = None,
    horizon_days: int = 30,
) -> list[WorklistItem]:
    """Return still-open applications due now or within the horizon."""
    root = Path(patterns_dir)
    today = as_of or date.today()
    horizon = today + timedelta(days=horizon_days)
    items: list[WorklistItem] = []

    for path in iter_application_files(root):
        metadata, _body = read_markdown(path)
        if metadata.get("outcome") != "still-open":
            continue
        applied_at = parse_date(metadata.get("applied_at"))
        if applied_at is None:
            continue
        due_at = applied_at + timedelta(days=REVIEW_WINDOW_DAYS)
        if due_at > horizon:
            continue
        items.append(
            WorklistItem(
                pattern_id=str(metadata.get("pattern_id", "")),
                source_repo=str(metadata.get("source_repo", "")),
                dec_ref=str(metadata.get("dec_ref", "")),
                applied_at=applied_at,
                due_at=due_at,
                days_until_due=(due_at - today).days,
                path=path,
            )
        )

    return sorted(items, key=lambda item: (item.due_at, item.pattern_id, item.source_repo))


def render_worklist(
    patterns_dir: str | Path,
    as_of: date | None = None,
    horizon_days: int = 30,
) -> str:
    today = as_of or date.today()
    items = outcome_worklist(patterns_dir, today, horizon_days)
    lines = [
        "90-day outcome worklist",
        f"as_of: {today.isoformat()}  horizon_days: {horizon_days}",
        "",
    ]
    if not items:
        lines.append("No still-open applications are due in this window.")
        lines.append("")
        return "\n".join(lines)

    header = f"{'due':<10} {'days':>5} {'pattern':<28} {'repo':<32} dec"
    lines.append(header)
    lines.append("-" * len(header))
    for item in items:
        lines.append(
            f"{item.due_at.isoformat():<10} {item.days_until_due:>5} "
            f"{item.pattern_id:<28} {item.source_repo:<32} {item.dec_ref}"
        )
    lines.append("")
    return "\n".join(lines)