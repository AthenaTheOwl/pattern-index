# System Map

## Inputs

- Portfolio repos with DEC markdown files under `decisions/`.
- `patterns/_taxonomy.yaml`, the canonical pattern ID list.
- Checked-in pattern application files under `patterns/<pattern_id>/applications/`.

## Processing

- `pattern_index.mine.dec_walker` reads DEC frontmatter and emits draft
  applications into `patterns/UNASSIGNED/applications/`.
- `pattern_index.validators` checks required fields, taxonomy membership,
  date shape, outcome values, and the 90-day outcome rule.
- `pattern_index.retro.writer` aggregates application files into a quarterly
  markdown report.

## Outputs

- Draft mined applications for human taxonomist review.
- Validated pattern application corpus.
- Quarterly retro files such as `patterns/2026-Q2-retro.md`.

## Boundaries

- The miner reads target repos only.
- The taxonomist moves `UNASSIGNED` entries into canonical pattern folders.
- The outcome tracker writes outcomes after the 90-day boundary.
- The retro writer reports what is present in the corpus; it does not invent
  new pattern IDs.
