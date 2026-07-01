from pathlib import Path

from pattern_index.mine.dec_walker import DecRecord, is_cross_domain


def _record(domain: str, references: tuple[str, ...], source_repo: str) -> DecRecord:
    return DecRecord(
        path=Path("decisions/DEC-014.md"),
        source_repo=source_repo,
        dec_id="DEC-014",
        domain=domain,
        references=references,
        applied_at="2026-04-10",
        title="Example",
    )


def test_reference_to_other_repo_is_cross_domain_even_when_domain_matches() -> None:
    # Domain equals the host, so the domain-mismatch branch does not trip;
    # the cross-repo reference is what should mark it as cross-domain.
    record = _record(
        domain="procurement",
        references=("supplier-risk-rag-agent#DEC-014",),
        source_repo="procurement",
    )

    assert is_cross_domain(record, "procurement") is True


def test_self_reference_in_same_repo_is_not_cross_domain() -> None:
    record = _record(
        domain="procurement",
        references=("procurement#DEC-002",),
        source_repo="procurement",
    )

    assert is_cross_domain(record, "procurement") is False
