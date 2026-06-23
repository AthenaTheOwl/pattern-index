"""Read-only summary of the committed patterns corpus.

Powers the no-arg `show` verb and the streamlit card browser. Reads the
checked-in `patterns/<pattern_id>/applications/*.md` corpus, ranks patterns
by how many cross-domain applications they carry, and surfaces which ones
actually worked on the 90-day outcome review.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from pattern_index.frontmatter import read_markdown
from pattern_index.validators import iter_application_files

OUTCOME_ORDER = ["worked", "still-open", "did-not-work", "abandoned"]


@dataclass(frozen=True)
class Application:
    pattern_id: str
    source_repo: str
    dec_ref: str
    target_domain: str
    applied_at: str
    outcome: str
    narrative: str


@dataclass(frozen=True)
class PatternRow:
    pattern_id: str
    applications: int
    worked: int
    repos: int
    outcomes: Counter


def default_patterns_dir() -> Path:
    """The committed patterns/ corpus at the repo root."""
    return Path(__file__).resolve().parents[2] / "patterns"


def load_applications(patterns_dir: str | Path | None = None) -> list[Application]:
    root = Path(patterns_dir) if patterns_dir is not None else default_patterns_dir()
    apps: list[Application] = []
    for path in iter_application_files(root):
        metadata, body = read_markdown(path)
        apps.append(
            Application(
                pattern_id=str(metadata.get("pattern_id", "")),
                source_repo=str(metadata.get("source_repo", "")),
                dec_ref=str(metadata.get("dec_ref", "")),
                target_domain=str(metadata.get("target_domain", "")),
                applied_at=str(metadata.get("applied_at", "")),
                outcome=str(metadata.get("outcome", "")),
                narrative=_narrative(body),
            )
        )
    return apps


def rank_patterns(apps: list[Application]) -> list[PatternRow]:
    """Rank patterns by application count, then by how many worked."""
    by_pattern: dict[str, list[Application]] = {}
    for app in apps:
        by_pattern.setdefault(app.pattern_id, []).append(app)

    rows: list[PatternRow] = []
    for pattern_id, group in by_pattern.items():
        outcomes = Counter(app.outcome for app in group)
        rows.append(
            PatternRow(
                pattern_id=pattern_id,
                applications=len(group),
                worked=outcomes.get("worked", 0),
                repos=len({app.source_repo for app in group}),
                outcomes=outcomes,
            )
        )
    rows.sort(key=lambda r: (-r.applications, -r.worked, r.pattern_id))
    return rows


def headline(apps: list[Application], rows: list[PatternRow]) -> str:
    if not apps:
        return "no pattern applications in the corpus yet."

    worked = [a for a in apps if a.outcome == "worked"]
    closed = [a for a in apps if a.outcome in {"worked", "did-not-work", "abandoned"}]
    transferred = sorted(rows, key=lambda r: (-r.repos, -r.applications))[0]

    if worked:
        names = ", ".join(sorted({a.pattern_id for a in worked}))
        rate = f"{len(worked)}/{len(closed)}" if closed else f"{len(worked)}"
        return (
            f"of {len(closed)} closed reviews, {rate} transferred and held: {names}. "
            f"'{transferred.pattern_id}' shows the widest reach "
            f"({transferred.repos} repos, {transferred.applications} applications)."
        )
    return (
        f"'{transferred.pattern_id}' shows the widest reach "
        f"({transferred.repos} repos); no closed review has confirmed a transfer yet."
    )


def render(patterns_dir: str | Path | None = None) -> str:
    apps = load_applications(patterns_dir)
    rows = rank_patterns(apps)

    if not apps:
        return "pattern index: no committed applications found.\n"

    repos = sorted({a.source_repo for a in apps})
    closed = sum(1 for a in apps if a.outcome != "still-open")

    lines: list[str] = []
    lines.append("cross-domain pattern index")
    lines.append(
        f"{len(apps)} applications  -  {len(rows)} patterns  -  "
        f"{len(repos)} source repos  -  {closed} closed reviews"
    )
    lines.append("")

    header = f"{'pattern':<28} {'apps':>4} {'repos':>5} {'worked':>6}  outcomes"
    lines.append(header)
    lines.append("-" * len(header))
    for row in rows:
        breakdown = ", ".join(
            f"{name} {row.outcomes[name]}"
            for name in OUTCOME_ORDER
            if row.outcomes.get(name)
        )
        lines.append(
            f"{row.pattern_id:<28} {row.applications:>4} {row.repos:>5} "
            f"{row.worked:>6}  {breakdown}"
        )

    lines.append("")
    lines.append(f"finding: {headline(apps, rows)}")
    lines.append("")
    return "\n".join(lines)


def _narrative(body: str) -> str:
    for block in body.split("\n\n"):
        text = block.strip()
        if text and not text.startswith("#"):
            return " ".join(text.split())
    return ""
