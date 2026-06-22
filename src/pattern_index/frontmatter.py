"""Small frontmatter parser for the v0.1 markdown corpus."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def read_markdown(path: Path) -> tuple[dict[str, Any], str]:
    return split_frontmatter(path.read_text(encoding="utf-8"))


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break

    if end_index is None:
        return {}, text

    metadata = parse_yaml_subset("\n".join(lines[1:end_index]))
    body = "\n".join(lines[end_index + 1 :]).lstrip("\n")
    return metadata, body


def parse_yaml_subset(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if current_key and stripped.startswith("- "):
            value = parse_scalar(stripped[2:].strip())
            existing = data.setdefault(current_key, [])
            if not isinstance(existing, list):
                data[current_key] = [existing]
                existing = data[current_key]
            existing.append(value)
            continue

        if ":" not in line:
            current_key = None
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            current_key = None
            continue

        if value == "":
            data[key] = []
            current_key = key
        else:
            data[key] = parse_scalar(value)
            current_key = None

    return data


def parse_scalar(value: str) -> Any:
    if value in {"null", "Null", "NULL", "~"}:
        return None
    if value in {"true", "True", "TRUE"}:
        return True
    if value in {"false", "False", "FALSE"}:
        return False
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def dump_frontmatter(metadata: dict[str, Any], body: str) -> str:
    lines = ["---"]
    for key, value in metadata.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {format_scalar(item)}")
        else:
            lines.append(f"{key}: {format_scalar(value)}")
    lines.append("---")
    lines.append("")
    lines.append(body.rstrip())
    lines.append("")
    return "\n".join(lines)


def format_scalar(value: Any) -> str:
    if value is None:
        return "null"
    text = str(value)
    if text == "" or any(char in text for char in [":", "#", '"']):
        escaped = text.replace('"', '\\"')
        return f'"{escaped}"'
    return text
