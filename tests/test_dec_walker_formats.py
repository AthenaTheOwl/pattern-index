from pathlib import Path

import pytest

from pattern_index.frontmatter import read_markdown
from pattern_index.mine.dec_walker import iter_dec_records, mine_repo

FORMATS_REPO = Path(__file__).parent / "fixtures" / "dec_formats"
REPO_ROOT = Path(__file__).resolve().parents[1]


def _records_by_id() -> dict:
    return {record.dec_id: record for record in iter_dec_records(FORMATS_REPO)}


@pytest.mark.parametrize(
    ("dec_id", "applied_at"),
    [
        ("DEC-PIX-001", "2026-06-21"),  # front matter below the H1
        ("DEC-CDCP-001-dec-coverage-required-per-shipped-r-star", "2026-05-24"),
        ("DEC-CAL-001", "2026-06-21"),  # - **date:** value
        ("DEC-PVP-001", "2026-06-20"),  # **Date**: value
        ("DEC-GRDS-001", "2026-06-20"),  # Date: value
        ("DEC-PM-001", "2026-06-22"),  # - Date: value
        ("DEC-AKI-001", "2026-09-23"),  # ## Status section
    ],
)
def test_each_ledger_format_parses_with_its_date(dec_id: str, applied_at: str) -> None:
    records = _records_by_id()

    assert dec_id in records
    assert records[dec_id].applied_at == applied_at


def test_records_without_domain_are_kept_and_readme_is_skipped() -> None:
    records = _records_by_id()

    assert len(records) == 7
    assert records["DEC-CAL-001"].domain == ""
    assert records["DEC-PIX-001"].domain == "pattern-index-governance"
    assert records["DEC-AKI-001"].title.startswith("DEC-AKI-001")


def test_front_matter_below_heading_is_mined_as_cross_domain(tmp_path: Path) -> None:
    written = mine_repo(FORMATS_REPO, tmp_path / "patterns")

    assert [path.name for path in written] == ["dec-formats-dec-pix-001.md"]
    metadata, _body = read_markdown(written[0])
    assert metadata["target_domain"] == "pattern-index-governance"
    assert metadata["applied_at"] == "2026-06-21"


def _sibling_repos() -> list[Path]:
    return sorted(
        path.parent
        for path in REPO_ROOT.parent.glob("*/decisions")
        if path.is_dir() and path.parent.resolve() != REPO_ROOT
    )


@pytest.mark.skipif(not _sibling_repos(), reason="no sibling repo checkouts next to this one")
def test_sibling_ledgers_parse_into_records() -> None:
    # This counts parsed records, not mined candidates. No current sibling
    # record carries `domain:` or `references:`, so `mine` writes no
    # candidates from them today.
    total = sum(len(list(iter_dec_records(repo))) for repo in _sibling_repos())

    assert total > 0


def _ledger(tmp_path: Path, files: dict[str, str]) -> Path:
    repo = tmp_path / "ledger"
    (repo / "decisions").mkdir(parents=True)
    for name, text in files.items():
        (repo / "decisions" / name).write_text(text, encoding="utf-8")
    return repo


def test_adr_style_record_with_front_matter_falls_back_to_file_stem(tmp_path: Path) -> None:
    repo = _ledger(
        tmp_path,
        {
            "0001-use-x.md": "---\ndomain: finance\ndate: 2026-01-01\n---\n\n# Use X\n",
            "README.md": "# Decisions\n\nOne file per decision.\n",
        },
    )

    records = list(iter_dec_records(repo))
    assert [record.dec_id for record in records] == ["0001-use-x"]

    written = mine_repo(repo, tmp_path / "patterns", primary_domain="ledger")
    assert [path.name for path in written] == ["ledger-0001-use-x.md"]


def test_plain_prose_field_lines_do_not_make_a_record_cross_domain(tmp_path: Path) -> None:
    repo = _ledger(
        tmp_path,
        {
            "DEC-X-001.md": "# DEC-X-001 a\n\nReferences: see the spec for context.\n",
            "DEC-X-002.md": "# DEC-X-002 b\n\n- **References:** DEC-X-001\n",
            "DEC-X-003.md": "# DEC-X-003 c\n\nDomain: this decision covers the whole repo\n",
            "DEC-X-004.md": "# DEC-X-004 d\n\n**References:** other-repo#DEC-007\n",
        },
    )

    records = {record.dec_id: record for record in iter_dec_records(repo)}
    assert records["DEC-X-001"].references == ()
    assert records["DEC-X-003"].domain == ""
    assert records["DEC-X-002"].references == ("DEC-X-001",)

    written = mine_repo(repo, tmp_path / "patterns", primary_domain="ledger")
    assert [path.name for path in written] == ["ledger-dec-x-004.md"]


def test_date_style_ids_keep_their_full_date(tmp_path: Path) -> None:
    repo = _ledger(
        tmp_path,
        {
            "DEC-2026-06-21-dated.md": "# DEC-2026-06-21 decision\n\nDate: 2026-06-21\n",
            "DEC-2026-07-02-dated.md": "# DEC-2026-07-02 decision\n\nDate: 2026-07-02\n",
        },
    )

    assert [record.dec_id for record in iter_dec_records(repo)] == [
        "DEC-2026-06-21",
        "DEC-2026-07-02",
    ]
