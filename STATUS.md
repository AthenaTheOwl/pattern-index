# Status

## Current state

- v0.1 ships a typed pattern application corpus under `patterns/` (15 applications across 9 repos).
- The Python CLI can mine DEC frontmatter, validate the corpus, write a quarterly retro, list 90-day outcome reviews, and print a ranked corpus summary (`show`, date-filtered with `show --as-of`).
- The checked-in report artifact is `patterns/2026-Q2-retro.md`.
- Contract gates are available through `python -m pytest` and the three scripts in `scripts/`.

## Known limits

- The miner reads DEC fields from front matter (leading or under the H1), `**Field:**` and `Field:` lines under the title, and `## Status` / `## Date` sections. It does not read the decision prose, so a record without `domain:` or `references:` is parsed but never mined as cross-domain.
- Pattern ID assignment remains manual; mined entries start as `UNASSIGNED`.
- The bundled corpus is a seed data report, not a full portfolio sweep. Ten of its 15 applications are illustrative seed rows marked `provenance: seed-illustrative`; their DEC ids and dates were not observed in the source repos. `show` reports how much of each count they carry.
- Outcome checks use calendar days and do not model business-day exceptions.
- Date-provenance checks (an outcome recorded before its application file was first committed, an application dated before its source repo's first commit) need full git history and sibling checkouts; they stand down in shallow clones such as CI's default checkout.

## Next feature queue

- Mine another tranche after the July outcome reviews close.
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
