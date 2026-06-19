# Tasks — Foundation

## PR 0002 — schema, taxonomy seed, miner skeleton

- [ ] Write `schemas/pattern_application.schema.json` matching
      R-PIX-001.
- [ ] Add `patterns/_taxonomy.yaml` seeded with 5 hand-curated
      pattern IDs from the existing portfolio (e.g., `eval-as-gate`,
      `typed-artifact-discipline`, `citation-faithful-extraction`,
      `dec-then-implement`, `voice-lint-as-spec-check`).
- [ ] Stub `src/pattern_index/__init__.py` and CLI entry point.
- [ ] Implement `src/pattern_index/mine/dec_walker.py`.
- [ ] Add `scripts/voice_lint.py` (copy from canonical template).
- [ ] Add `scripts/validate_schemas.py` and
      `scripts/validate_outcomes.py`.
- [ ] Add `pyproject.toml`.

## PR 0003 — first real mining pass and retro skeleton

- [ ] Run miner against `procurement-negotiation-lab/decisions/`.
- [ ] Hand-promote UNASSIGNED entries into real pattern_ids.
- [ ] Run miner against `supplier-risk-rag-agent/decisions/`.
- [ ] Implement `src/pattern_index/retro/writer.py`.
- [ ] Write `tests/test_dec_walker.py` against fixture DEC files.
- [ ] Write `tests/test_validate_outcomes.py` covering the 90-day
      cliff.

## PR 0004 — first quarterly retro

- [ ] Mine three more repos (`ai-field-brief`,
      `trace-to-eval-harness`, `chip-supply-chain-map`).
- [ ] Backfill outcomes for any applications older than 90 days.
- [ ] Run `python -m pattern_index retro --quarter 2026-Q3 \
      --out patterns/2026-Q3-retro.md`.
- [ ] Hand-edit narrative paragraphs.
- [ ] Land `patterns/2026-Q3-retro.md`.
- [ ] Add `decisions/DEC-PIX-001-taxonomy-curation-policy.md`
      recording why pattern IDs stay human-curated.
