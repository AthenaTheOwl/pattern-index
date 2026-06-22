"""DEC frontmatter mining for draft pattern applications."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re
from typing import Any, Iterable

from pattern_index.frontmatter import dump_frontmatter, read_markdown


@dataclass(frozen=True)
class DecRecord:
    path: Path
    source_repo: str
    dec_id: str
    domain: str
    references: tuple[str, ...]
    applied_at: str
    title: str


def mine_repo(
    repo: str | Path,
    out: str | Path,
    primary_domain: str | None = None,
) -> list[Path]:
    repo_path = Path(repo)
    out_path = Path(out)
    source_repo = slug(repo_path.name)
    host_domain = primary_domain or read_primary_domain(repo_path)
    written: list[Path] = []

    for record in iter_dec_records(repo_path, source_repo):
        if not is_cross_domain(record, host_domain):
            continue
        target_dir = out_path / "UNASSIGNED" / "applications"
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{source_repo}-{slug(record.dec_id)}.md"
        target.write_text(candidate_markdown(record), encoding="utf-8")
        written.append(target)

    return written


def iter_dec_records(repo_path: Path, source_repo: str | None = None) -> Iterable[DecRecord]:
    decisions_dir = repo_path / "decisions"
    if not decisions_dir.exists():
        return []

    repo_slug = source_repo or slug(repo_path.name)
    records: list[DecRecord] = []
    for path in sorted(decisions_dir.glob("*.md")):
        record = parse_dec_record(path, repo_slug)
        if record is not None:
            records.append(record)
    return records


def parse_dec_record(path: Path, source_repo: str) -> DecRecord | None:
    metadata, body = read_markdown(path)
    dec_id = str(metadata.get("id") or path.stem)
    domain = str(metadata.get("domain") or "")
    if not dec_id or not domain:
        return None

    references = tuple(normalize_references(metadata.get("references")))
    applied_at = str(
        metadata.get("applied_at")
        or metadata.get("date")
        or metadata.get("created_at")
        or date.today().isoformat()
    )
    title = first_heading(body) or path.stem
    return DecRecord(
        path=path,
        source_repo=source_repo,
        dec_id=dec_id,
        domain=domain,
        references=references,
        applied_at=applied_at,
        title=title,
    )


def normalize_references(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    return [part.strip() for part in re.split(r"[,;]", text) if part.strip()]


def is_cross_domain(record: DecRecord, primary_domain: str) -> bool:
    host_domain = primary_domain.strip().lower()
    record_domain = record.domain.strip().lower()
    if host_domain and record_domain and record_domain != host_domain:
        return True

    for reference in record.references:
        repo_name = reference.split("#", 1)[0].strip()
        if repo_name and slug(repo_name) != record.source_repo:
            return True

    return False


def candidate_markdown(record: DecRecord) -> str:
    metadata = {
        "pattern_id": "UNASSIGNED",
        "source_repo": record.source_repo,
        "dec_ref": record.dec_id,
        "target_domain": record.domain,
        "applied_at": record.applied_at,
        "outcome": "still-open",
        "outcome_recorded_at": None,
        "outcome_evidence": [
            "Still open; mined candidate has not reached human outcome review."
        ],
    }
    body = (
        "## Narrative\n\n"
        f"Mined from {record.source_repo} {record.dec_id}. "
        "A human taxonomist must assign the pattern ID before this file is checked in."
    )
    return dump_frontmatter(metadata, body)


def read_primary_domain(repo_path: Path) -> str:
    agents_path = repo_path / "AGENTS.md"
    if agents_path.exists():
        text = agents_path.read_text(encoding="utf-8", errors="ignore")
        for pattern in [
            r"primary domain\s*:\s*([A-Za-z0-9_.-]+)",
            r"domain\s*:\s*([A-Za-z0-9_.-]+)",
        ]:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(1)
    return slug(repo_path.name)


def first_heading(body: str) -> str | None:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return None


def slug(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    return lowered.strip("-") or "unknown"
