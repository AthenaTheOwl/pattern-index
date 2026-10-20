# Status

## Current state

- v0.1 ships a typed pattern application corpus under `patterns/` (15 applications across 9 repos).
- The Python CLI can mine DEC record fields, validate the corpus, write a quarterly retro, list 90-day outcome reviews, and print a ranked corpus summary (`show`, date-filtered with `show --as-of`).
- The checked-in report artifact is `patterns/2026-Q2-retro.md`.
- Contract gates are available through `python -m pytest` and the four scripts in `scripts/`.

## Known limits

- The miner reads DEC fields from front matter (leading or under the H1), `**Field:**` and `Field:` lines under the title, and `## Status` / `## Date` sections; `domain:` and `references:` count only from front matter or `**Field:**` lines. It does not read the decision prose, so a record without `domain:` or `references:` is parsed but never mined as cross-domain. No current sibling record carries either field, so `mine` writes no candidates from the sibling ledgers today.
- Pattern ID assignment remains manual; mined entries start as `UNASSIGNED`.
- The bundled corpus is a seed data report, not a full portfolio sweep. Ten of its 15 applications are illustrative seed rows marked `provenance: seed-illustrative`; nine of the ten cite DEC ids that do not exist in their source repos, nine have `applied_at` dates before the source repo's first commit, and four have outcome dates before the file was committed. `show` reports how much of each count they carry.
- Outcome checks use calendar days and do not model business-day exceptions.
- Date-provenance checks (an outcome recorded before its application file was first committed, an application dated before its source repo's first commit) need full git history and sibling checkouts; they stand down in shallow clones such as CI's default checkout.

## Next feature queue

- Mine another tranche after the July outcome reviews close.
- Add a compact retro diff that compares the current quarter to the prior quarter.

- Resolve factory defect: claude_code review requested patch; inspect defect log
