# Acceptance — v0 Foundation

"v0 done" means the miner walks a real portfolio repo, emits typed
candidate entries, a human can promote them to real pattern IDs, and
the validator chain refuses to merge entries past the 90-day cliff
without outcomes.

## Commands a reviewer must be able to run

```bash
python -m pip install -e .[dev]

python -m pattern_index mine \
  --repo ../procurement-negotiation-lab \
  --out patterns/

python -m pattern_index validate patterns/

python -m pattern_index retro \
  --quarter 2026-Q3 \
  --out patterns/2026-Q3-retro.md
```

## Gates that must pass

- `python -m pytest` exits 0 with the fixture-based DEC walker test.
- `python scripts/voice_lint.py patterns/` exits 0.
- `python scripts/validate_schemas.py patterns/` exits 0.
- `python scripts/validate_outcomes.py patterns/` exits 0.

## Artifacts that must exist

- `patterns/_taxonomy.yaml` with at least 5 hand-curated IDs.
- At least 10 mined applications under `patterns/` from at least
  three different source repos.
- `patterns/2026-Q3-retro.md` — the first real quarterly retro.
- `decisions/DEC-PIX-001-taxonomy-curation-policy.md`.

## Out of scope for v0

- Embedding-based pattern similarity.
- Web UI.
- Cross-repo PR generation.
- Auto-fill of outcome fields.

## What "done" feels like

A reader picks up `patterns/2026-Q3-retro.md` and learns, in under
three minutes, which day-job patterns have transferred into AI builds
this quarter, which have failed, and what the taxonomist proposes
adding to `_taxonomy.yaml` next quarter. The proof is in the file.
