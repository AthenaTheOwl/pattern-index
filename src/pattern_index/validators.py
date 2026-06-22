"""Corpus validation shared by CLI and scripts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import re
from typing import Iterable

from pattern_index.frontmatter import read_markdown

OUTCOMES = {"worked", "did-not-work", "still-open", "abandoned"}
REQUIRED_FIELDS = {
    "pattern_id",
    "source_repo",
    "dec_ref",
    "target_domain",
    "applied_at",
    "outcome",
    "outcome_recorded_at",
    "outcome_evidence",
}
BANNED_WORDS = {"leverage", "synergy", "best-in-class", "seamless"}


@dataclass(frozen=True)
class ValidationError:
    path: Path
    message: str

    def render(self) -> str:
        return f"{self.path}: {self.message}"


def load_taxonomy(patterns_dir: str | Path) -> set[str]:
    taxonomy_path = Path(patterns_dir) / "_taxonomy.yaml"
    metadata = _parse_taxonomy_file(taxonomy_path)
    ids = metadata.get("pattern_ids", [])
    return {str(item) for item in ids}


def validate_schema(patterns_dir: str | Path) -> list[ValidationError]:
    root = Path(patterns_dir)
    taxonomy = load_taxonomy(root)
    errors: list[ValidationError] = []

    if not taxonomy:
        errors.append(ValidationError(root / "_taxonomy.yaml", "no pattern_ids found"))

    for path in iter_application_files(root):
        metadata, _body = read_markdown(path)
        missing = sorted(REQUIRED_FIELDS - set(metadata))
        if missing:
            errors.append(ValidationError(path, f"missing fields: {', '.join(missing)}"))
            continue

        pattern_id = str(metadata["pattern_id"])
        if pattern_id not in taxonomy:
            errors.append(ValidationError(path, f"unknown pattern_id: {pattern_id}"))

        folder_id = path.parent.parent.name
        if folder_id != pattern_id:
            errors.append(
                ValidationError(path, f"folder '{folder_id}' does not match pattern_id")
            )

        outcome = str(metadata["outcome"])
        if outcome not in OUTCOMES:
            errors.append(ValidationError(path, f"invalid outcome: {outcome}"))

        for field in ["source_repo", "dec_ref", "target_domain"]:
            if not str(metadata[field]).strip():
                errors.append(ValidationError(path, f"{field} is blank"))

        if parse_date(metadata["applied_at"]) is None:
            errors.append(ValidationError(path, "applied_at must be YYYY-MM-DD"))

        recorded_at = metadata.get("outcome_recorded_at")
        if recorded_at is not None and parse_date(recorded_at) is None:
            errors.append(
                ValidationError(path, "outcome_recorded_at must be YYYY-MM-DD or null")
            )

        evidence = metadata.get("outcome_evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(ValidationError(path, "outcome_evidence must be a list"))

    return errors


def validate_outcomes(
    patterns_dir: str | Path,
    as_of: date | None = None,
) -> list[ValidationError]:
    root = Path(patterns_dir)
    today = as_of or date.today()
    cutoff = today - timedelta(days=90)
    errors: list[ValidationError] = []

    for path in iter_application_files(root):
        metadata, _body = read_markdown(path)
        outcome = str(metadata.get("outcome", "")).strip()
        applied_at = parse_date(metadata.get("applied_at"))
        if not outcome:
            errors.append(ValidationError(path, "outcome is blank"))
            continue
        if outcome not in OUTCOMES:
            errors.append(ValidationError(path, f"invalid outcome: {outcome}"))
            continue
        if applied_at is None:
            errors.append(ValidationError(path, "applied_at must be YYYY-MM-DD"))
            continue

        if applied_at <= cutoff and outcome == "still-open":
            errors.append(
                ValidationError(path, "still-open outcome is older than 90 days")
            )

        if outcome != "still-open":
            recorded_at = metadata.get("outcome_recorded_at")
            evidence = metadata.get("outcome_evidence")
            if parse_date(recorded_at) is None:
                errors.append(
                    ValidationError(path, "closed outcome needs outcome_recorded_at")
                )
            if not isinstance(evidence, list) or not evidence:
                errors.append(ValidationError(path, "closed outcome needs evidence"))

    return errors


def lint_voice(paths: Iterable[str | Path]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for path in iter_markdown_paths(paths):
        text = path.read_text(encoding="utf-8", errors="ignore")
        lowered = text.lower()
        for word in BANNED_WORDS:
            if word in lowered:
                errors.append(ValidationError(path, f"banned word: {word}"))
        if re.search(r"\bnot\b.{0,80}\bbut\b", lowered, flags=re.DOTALL):
            errors.append(ValidationError(path, "antithetical reversal phrasing"))
    return errors


def iter_application_files(patterns_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(patterns_dir.glob("*/applications/*.md")):
        if path.parts[-3] == "UNASSIGNED":
            continue
        files.append(path)
    return files


def iter_markdown_paths(paths: Iterable[str | Path]) -> Iterable[Path]:
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            continue
        if path.is_file() and path.suffix.lower() == ".md":
            yield path
        elif path.is_dir():
            yield from sorted(path.rglob("*.md"))


def parse_date(value: object) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _parse_taxonomy_file(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    from pattern_index.frontmatter import parse_yaml_subset

    return parse_yaml_subset(path.read_text(encoding="utf-8"))
