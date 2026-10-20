"""DEC record field mining for draft pattern applications."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re
from typing import Any, Iterable

from pattern_index.frontmatter import dump_frontmatter, split_frontmatter


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


# Longest DEC-shaped prefix, so a date-style id such as DEC-2026-06-21 is not
# cut to DEC-2026.
DEC_ID_RE = re.compile(r"\bDEC-(?:[A-Za-z0-9]+-)*[0-9]+\b", re.IGNORECASE)
ISO_DATE_RE = re.compile(r"\b[0-9]{4}-[0-9]{2}-[0-9]{2}\b")
FIELD_KEYS = {
    "id",
    "date",
    "status",
    "domain",
    "references",
    "applied_at",
    "created_at",
}
BOLD_FIELD_RE = re.compile(
    r"^\s*(?:[-*]\s+)?\*\*(?P<key>[A-Za-z][A-Za-z _-]*?)(?::\*\*|\*\*\s*:)\s*(?P<value>.*)$"
)
PLAIN_FIELD_RE = re.compile(
    r"^(?:[-*]\s+)?(?P<key>[A-Za-z][A-Za-z _-]*?)\s*:\s*(?P<value>.+)$"
)
FIELD_ALIASES = {"decided": "date"}
# Fields that decide cross-domain mining. A plain `Field: value` line is too
# easily ordinary prose ("Domain: this covers the whole repo"), so these are
# read only from front matter or bold `**Field:**` lines.
STRICT_FIELD_KEYS = {"domain", "references"}
RECORD_FIELD_KEYS = {"domain", "references", "date", "status", "applied_at", "created_at"}


def read_dec_metadata(path: Path) -> tuple[dict[str, Any], str]:
    """Read a DEC record's fields from any of the ledger formats in use.

    The sibling ledgers write the same fields several ways: a leading `---`
    front-matter block, a front-matter block under the H1, `**Field:** value`
    or `**Field**: value` lines under the H1, plain `Field: value` lines (bare
    or bulleted), and `## Status` / `## Date` sections. Front matter wins; the
    other shapes only fill fields it did not set. `domain` and `references`
    are read only from front matter or bold field lines. `domain` is optional: a
    record without one is still a record, and is cross-domain only through
    its references.
    """
    text = path.read_text(encoding="utf-8")
    metadata, body = split_frontmatter(text)
    if not metadata:
        lines = text.splitlines()
        start = 0
        while start < len(lines) and (
            not lines[start].strip() or lines[start].lstrip().startswith("# ")
        ):
            start += 1
        if start < len(lines) and lines[start].strip() == "---":
            heading = "\n".join(lines[:start]).strip()
            metadata, rest = split_frontmatter("\n".join(lines[start:]))
            if metadata:
                body = f"{heading}\n\n{rest}" if heading else rest

    fields = dict(metadata)
    preamble: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            break
        preamble.append(line)
    for line in preamble:
        bold = BOLD_FIELD_RE.match(line)
        match = bold or PLAIN_FIELD_RE.match(line.strip())
        if not match:
            continue
        key = re.sub(r"[ -]+", "_", match.group("key").strip().lower())
        key = FIELD_ALIASES.get(key, key)
        if key in STRICT_FIELD_KEYS and not bold:
            continue
        value = match.group("value").strip()
        if key in FIELD_KEYS and value and key not in fields:
            fields[key] = value

    for key in ("date", "status"):
        section = _section_text(body, key)
        if section and key not in fields:
            fields[key] = section
    if "date" in fields and "date" not in metadata:
        found = ISO_DATE_RE.search(str(fields["date"]))
        if found:
            fields["date"] = found.group(0)
        else:
            del fields["date"]
    if not any(k in fields for k in ("applied_at", "date", "created_at")):
        found = ISO_DATE_RE.search(str(fields.get("status") or ""))
        if found:
            fields["date"] = found.group(0)
    return fields, body


def _section_text(body: str, name: str) -> str:
    lines = body.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("## ") and line[3:].strip().lower() == name:
            collected: list[str] = []
            for follow in lines[index + 1 :]:
                if follow.startswith("#"):
                    break
                if follow.strip():
                    collected.append(follow.strip())
            return " ".join(collected)
    return ""


def dec_id_for(metadata: dict[str, Any], body: str, path: Path) -> str | None:
    if metadata.get("id"):
        return str(metadata["id"])
    heading = first_heading(body) or ""
    for source in (heading, path.stem):
        match = DEC_ID_RE.search(source)
        if match:
            return match.group(0).upper()
    # An ADR-style file (0001-use-x.md) with real record fields is still a
    # record; a file with neither a DEC id nor fields (a README) is not.
    if any(metadata.get(key) for key in RECORD_FIELD_KEYS):
        return path.stem
    return None


def parse_dec_record(path: Path, source_repo: str) -> DecRecord | None:
    metadata, body = read_dec_metadata(path)
    dec_id = dec_id_for(metadata, body, path)
    domain = str(metadata.get("domain") or "")
    if not dec_id:
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
        # A bare DEC id names no repo, so it is a same-repo reference.
        if DEC_ID_RE.fullmatch(repo_name):
            continue
        if repo_name and slug(repo_name) != record.source_repo:
            return True

    return False


def candidate_markdown(record: DecRecord) -> str:
    metadata = {
        "pattern_id": "UNASSIGNED",
        "source_repo": record.source_repo,
        "dec_ref": record.dec_id,
        "target_domain": record.domain or "UNASSIGNED",
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
