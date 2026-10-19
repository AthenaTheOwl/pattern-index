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
def test_mining_sibling_ledgers_extracts_records() -> None:
    total = sum(len(list(iter_dec_records(repo))) for repo in _sibling_repos())

    assert total > 0
