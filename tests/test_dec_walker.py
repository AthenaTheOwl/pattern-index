from pathlib import Path

from pattern_index.frontmatter import read_markdown
from pattern_index.mine.dec_walker import mine_repo


def test_mine_repo_writes_unassigned_candidate(tmp_path: Path) -> None:
    fixture_repo = Path(__file__).parent / "fixtures"
    written = mine_repo(fixture_repo, tmp_path / "patterns")

    assert len(written) == 1
    target = written[0]
    assert target.name == "fixtures-dec-001.md"
    assert target.parent.name == "applications"
    assert target.parent.parent.name == "UNASSIGNED"

    metadata, body = read_markdown(target)
    assert metadata["pattern_id"] == "UNASSIGNED"
    assert metadata["source_repo"] == "fixtures"
    assert metadata["dec_ref"] == "DEC-001"
    assert metadata["target_domain"] == "rag-eval-discipline"
    assert metadata["outcome"] == "still-open"
    assert "human taxonomist" in body
