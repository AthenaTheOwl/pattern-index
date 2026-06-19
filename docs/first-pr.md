# First PR (after scaffold)

The literal first PR after this v0 scaffold is PR 0002: schema,
taxonomy seed, and DEC-miner skeleton.

## Scope

One PR. The miner reads but does not yet promote. The taxonomy seed
captures 5 patterns that already exist informally across the
portfolio. The validators run on the seed itself.

## Files added

```
schemas/pattern_application.schema.json
patterns/_taxonomy.yaml
patterns/eval-as-gate/.gitkeep
patterns/typed-artifact-discipline/.gitkeep
patterns/citation-faithful-extraction/.gitkeep
patterns/dec-then-implement/.gitkeep
patterns/voice-lint-as-spec-check/.gitkeep
patterns/UNASSIGNED/.gitkeep
src/pattern_index/__init__.py
src/pattern_index/__main__.py
src/pattern_index/cli.py
src/pattern_index/mine/__init__.py
src/pattern_index/mine/dec_walker.py
scripts/voice_lint.py
scripts/validate_schemas.py
scripts/validate_outcomes.py
tests/fixtures/decisions/DEC-001-eval-as-gate-applied.md
tests/test_dec_walker.py
pyproject.toml
```

## Files changed

```
README.md         # add the "How to run" section with mine command
AGENTS.md         # uncomment the gate block
```

## Why this scope

The seed taxonomy is the load-bearing decision in this PR. Five IDs
is the right number for v0: enough to make the schema feel real,
small enough that the human taxonomist holds the whole list in
working memory when promoting UNASSIGNED entries.

The miner walks but does not assign. That separation is what makes
the corpus trustworthy later.

## Verification

```bash
python -m pip install -e .[dev]
python -m pytest
python scripts/voice_lint.py README.md AGENTS.md patterns/
python scripts/validate_schemas.py patterns/
python -m pattern_index mine \
  --repo tests/fixtures \
  --out /tmp/mined/
```

The last command should exit 0 and write at least one file under
`/tmp/mined/UNASSIGNED/applications/`.

## Out of scope (deferred to PR 0003)

- The retro writer.
- Mining against real portfolio repos.
- The outcome backfill workflow.

## Decision record

PR 0002 lands `decisions/DEC-PIX-000-static-mining-no-llm.md` naming
why the miner uses static frontmatter parsing rather than LLM-driven
classification: cheaper, deterministic, reproducible, and the cost
(taxonomy must be human-curated) is acceptable at quarterly cadence.
