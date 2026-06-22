# Status

## Current state

- v0.1 ships a typed pattern application corpus under `patterns/`.
- The Python CLI can mine DEC frontmatter, validate the corpus, and write a quarterly retro.
- The checked-in report artifact is `patterns/2026-Q2-retro.md`.
- Contract gates are available through `python -m pytest` and the three scripts in `scripts/`.

## Known limits

- The miner only reads static DEC frontmatter and does not inspect DEC body text.
- Pattern ID assignment remains manual; mined entries start as `UNASSIGNED`.
- The bundled corpus is a seed data report, not a full portfolio sweep.
- Outcome checks use calendar days and do not model business-day exceptions.

## Next feature queue

- Mine the next three portfolio repos and promote new candidates by hand.
- Add a worklist command for entries that cross the 90-day outcome boundary.
- Add fixture coverage for DEC records with missing frontmatter.
- Add a compact retro diff that compares the current quarter to the prior quarter.

- Resolve factory defect: missing PRODUCT_BRIEF.md,SYSTEM_MAP.md
- Resolve factory defect: missing reports/*.jsonl
- Resolve factory defect: PRODUCT_BRIEF.md is required for active repos
- Resolve factory defect: SYSTEM_MAP.md is required for active repos
- Resolve factory defect: expected file 'PRODUCT_BRIEF.md' is missing
- Resolve factory defect: expected file 'SYSTEM_MAP.md' is missing
- Resolve factory defect: expected file 'pattern_index/cli.py' is missing
- Resolve factory defect: expected glob 'reports/*.jsonl' matched no files
- Resolve factory defect: module 'cli' declares source 'pattern_index/cli.py', but it is missing
- Resolve factory defect: module 'model' declares source 'pattern_index/model.py', but it is missing
- Resolve factory defect: module 'report' declares source 'pattern_index/scoring.py', but it is missing
- Resolve factory defect: claude_code review requested patch; inspect defect log
