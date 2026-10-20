import importlib.util
import os
import subprocess
from pathlib import Path

from pattern_index.cli import main
from pattern_index.frontmatter import dump_frontmatter
from pattern_index.validators import validate_record_dates


def _git(repo: Path, *args: str, when: str | None = None) -> None:
    env = dict(os.environ)
    env.update(
        GIT_AUTHOR_NAME="fixture",
        GIT_AUTHOR_EMAIL="fixture@example.invalid",
        GIT_COMMITTER_NAME="fixture",
        GIT_COMMITTER_EMAIL="fixture@example.invalid",
    )
    if when:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = f"{when}T12:00:00+00:00"
    subprocess.run(
        ["git", "-c", "commit.gpgsign=false", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        env=env,
    )


def _write(
    patterns: Path,
    name: str,
    *,
    applied_at: str,
    recorded_at: str | None,
    source_repo: str = "source-repo",
    seed: bool = False,
) -> Path:
    metadata = {
        "pattern_id": "eval-as-gate",
        "source_repo": source_repo,
        "dec_ref": "DEC-001",
        "target_domain": "testing",
        "applied_at": applied_at,
        "outcome": "worked" if recorded_at else "still-open",
        "outcome_recorded_at": recorded_at,
        "outcome_evidence": ["Fixture evidence."],
    }
    if seed:
        metadata["provenance"] = "seed-illustrative"
    target = patterns / "eval-as-gate" / "applications" / f"{name}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(dump_frontmatter(metadata, "Fixture."), encoding="utf-8")
    return target


def _index_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "index"
    (repo / "patterns").mkdir(parents=True)
    _git(repo, "init", "-q")
    return repo


def test_outcome_recorded_before_the_record_existed_is_an_error(tmp_path: Path) -> None:
    repo = _index_repo(tmp_path)
    patterns = repo / "patterns"
    _write(patterns, "early", applied_at="2026-01-05", recorded_at="2026-06-03")
    _write(patterns, "later", applied_at="2026-01-05", recorded_at="2026-07-01")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "add", when="2026-06-21")

    errors, warnings = validate_record_dates(patterns)

    assert warnings == []
    assert [(e.path.name, e.message) for e in errors] == [
        (
            "early.md",
            "outcome_recorded_at 2026-06-03 precedes this record's first commit (2026-06-21)",
        )
    ]


def test_applied_before_the_source_repo_existed_is_an_error(tmp_path: Path) -> None:
    repo = _index_repo(tmp_path)
    patterns = repo / "patterns"
    _write(patterns, "before", applied_at="2026-02-12", recorded_at=None)
    _write(patterns, "after", applied_at="2026-05-01", recorded_at=None, source_repo="other")
    source = tmp_path / "source-repo"
    source.mkdir()
    _git(source, "init", "-q")
    _git(source, "commit", "-q", "--allow-empty", "-m", "first", when="2026-04-29")
    other = tmp_path / "other"
    other.mkdir()
    _git(other, "init", "-q")
    _git(other, "commit", "-q", "--allow-empty", "-m", "first", when="2026-04-29")

    errors, _warnings = validate_record_dates(patterns, repos_root=tmp_path)

    assert [(e.path.name, e.message) for e in errors] == [
        (
            "before.md",
            "applied_at 2026-02-12 precedes source-repo's first commit (2026-04-29)",
        )
    ]


def test_seed_rows_are_warnings_not_errors(tmp_path: Path) -> None:
    repo = _index_repo(tmp_path)
    patterns = repo / "patterns"
    _write(patterns, "seed", applied_at="2026-01-05", recorded_at="2026-06-03", seed=True)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "add", when="2026-06-21")

    errors, warnings = validate_record_dates(patterns)

    assert errors == []
    assert [w.path.name for w in warnings] == ["seed.md"]


def test_unchecked_when_history_is_unavailable(tmp_path: Path) -> None:
    patterns = tmp_path / "patterns"
    _write(patterns, "early", applied_at="2026-01-05", recorded_at="2026-01-06")

    # Not a git checkout, and no source repo under repos_root: nothing to compare.
    assert validate_record_dates(patterns, repos_root=tmp_path) == ([], [])


def test_shallow_clone_skips_the_creation_check(tmp_path: Path) -> None:
    repo = _index_repo(tmp_path)
    patterns = repo / "patterns"
    _write(patterns, "early", applied_at="2026-01-05", recorded_at="2026-06-03")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "add", when="2026-06-01")
    (patterns / "touch.txt").write_text("x", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "later", when="2026-10-01")
    shallow = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", f"file://{repo}", str(shallow)],
        check=True,
        capture_output=True,
    )

    # At depth 1 every file looks added at HEAD (2026-10-01), which would
    # flag a correct outcome date; the check must stand down instead.
    assert validate_record_dates(shallow / "patterns") == ([], [])


def test_dates_on_the_boundary_day_are_not_flagged(tmp_path: Path) -> None:
    repo = _index_repo(tmp_path)
    patterns = repo / "patterns"
    _write(patterns, "same-day", applied_at="2026-04-29", recorded_at="2026-06-21")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "add", when="2026-06-21")
    source = tmp_path / "source-repo"
    source.mkdir()
    _git(source, "init", "-q")
    _git(source, "commit", "-q", "--allow-empty", "-m", "first", when="2026-04-29")

    assert validate_record_dates(patterns, repos_root=tmp_path) == ([], [])


def test_shallow_source_repo_skips_the_applied_at_check(tmp_path: Path) -> None:
    patterns = tmp_path / "patterns"
    _write(patterns, "early", applied_at="2026-02-12", recorded_at=None)
    full = tmp_path / "full-source"
    full.mkdir()
    _git(full, "init", "-q")
    _git(full, "commit", "-q", "--allow-empty", "-m", "first", when="2026-01-01")
    _git(full, "commit", "-q", "--allow-empty", "-m", "later", when="2026-10-01")
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", f"file://{full}", str(tmp_path / "source-repo")],
        check=True,
        capture_output=True,
    )

    # At depth 1 the graft commit (2026-10-01) looks like the first commit,
    # which would flag a correct applied_at; the check must stand down.
    assert validate_record_dates(patterns, repos_root=tmp_path) == ([], [])


def _cli_corpus(tmp_path: Path, *, seed: bool) -> Path:
    repo = _index_repo(tmp_path)
    patterns = repo / "patterns"
    (patterns / "_taxonomy.yaml").write_text("pattern_ids:\n  - eval-as-gate\n", encoding="utf-8")
    _write(patterns, "early", applied_at="2026-01-05", recorded_at="2026-06-03", seed=seed)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "add", when="2026-06-21")
    return patterns


def _validate_outcomes_script():
    script = Path(__file__).resolve().parents[1] / "scripts" / "validate_outcomes.py"
    spec = importlib.util.spec_from_file_location("validate_outcomes_script", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main


def test_validate_cli_and_script_fail_on_a_real_row_date_error(tmp_path: Path, capsys) -> None:
    patterns = _cli_corpus(tmp_path, seed=False)

    assert main(["validate", str(patterns)]) == 1
    assert "precedes this record's first commit" in capsys.readouterr().out
    assert _validate_outcomes_script()([str(patterns)]) == 1
    assert "precedes this record's first commit" in capsys.readouterr().out


def test_validate_cli_and_script_warn_on_a_seed_row(tmp_path: Path, capsys) -> None:
    patterns = _cli_corpus(tmp_path, seed=True)

    assert main(["validate", str(patterns)]) == 0
    assert "WARN (seed-illustrative)" in capsys.readouterr().out
    assert _validate_outcomes_script()([str(patterns)]) == 0
    assert "WARN (seed-illustrative)" in capsys.readouterr().out


def test_validate_cli_defaults_repos_root_to_the_index_repo_parent(tmp_path: Path, capsys) -> None:
    repo = _index_repo(tmp_path)
    patterns = repo / "patterns"
    (patterns / "_taxonomy.yaml").write_text("pattern_ids:\n  - eval-as-gate\n", encoding="utf-8")
    _write(patterns, "before", applied_at="2026-02-12", recorded_at=None)
    source = tmp_path / "source-repo"
    source.mkdir()
    _git(source, "init", "-q")
    _git(source, "commit", "-q", "--allow-empty", "-m", "first", when="2026-04-29")

    assert main(["validate", str(patterns)]) == 1
    assert "precedes source-repo's first commit" in capsys.readouterr().out
    assert _validate_outcomes_script()([str(patterns)]) == 1
    assert "precedes source-repo's first commit" in capsys.readouterr().out
