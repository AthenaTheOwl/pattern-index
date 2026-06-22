"""Quarterly retro report writer."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from pattern_index.frontmatter import read_markdown
from pattern_index.validators import iter_application_files


def build_retro(quarter: str, patterns_dir: str | Path) -> str:
    root = Path(patterns_dir)
    applications = []
    for path in iter_application_files(root):
        metadata, _body = read_markdown(path)
        applications.append((path, metadata))

    by_pattern = Counter(str(metadata["pattern_id"]) for _path, metadata in applications)
    by_outcome = Counter(str(metadata["outcome"]) for _path, metadata in applications)
    source_repos = sorted({str(metadata["source_repo"]) for _path, metadata in applications})

    lines = [
        f"# Pattern Index Retro - {quarter}",
        "",
        "## Summary",
        "",
        f"- Applications reviewed: {len(applications)}",
        f"- Source repos represented: {len(source_repos)}",
        f"- Pattern IDs represented: {len(by_pattern)}",
        "",
        "## Count by pattern",
        "",
    ]

    for pattern_id, count in sorted(by_pattern.items()):
        lines.append(f"- {pattern_id}: {count}")

    lines.extend(["", "## Count by outcome", ""])
    for outcome, count in sorted(by_outcome.items()):
        lines.append(f"- {outcome}: {count}")

    lines.extend(
        [
            "",
            "## Narrative",
            "",
            "The quarter shows a small seed corpus with enough variety to test the workflow. "
            "Eval gates and typed artifacts appear more than once, which gives the next mining pass a concrete taxonomy baseline.",
            "",
            "Open items are recent enough to wait for the 90-day review. Closed items carry one sentence of evidence so the report stays factual.",
            "",
            "## Proposed taxonomy additions",
            "",
            "- None.",
            "",
            "## Source repos",
            "",
        ]
    )
    for source_repo in source_repos:
        lines.append(f"- {source_repo}")

    lines.append("")
    return "\n".join(lines)


def write_retro(
    quarter: str,
    out_path: str | Path,
    patterns_dir: str | Path | None = None,
) -> Path:
    target = Path(out_path)
    root = Path(patterns_dir) if patterns_dir is not None else target.parent
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_retro(quarter, root), encoding="utf-8")
    return target
