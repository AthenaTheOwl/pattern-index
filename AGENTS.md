# AGENTS.md — pattern-index

Operating contract for AI agents working in this repo. Conventions
match the rest of the AthenaTheOwl portfolio.

## What this repo is

A quarterly mining pass over portfolio DEC ledgers, plus a typed
schema for pattern applications, plus an outcome field that gets
filled in 90 days after the application was recorded.

The artifact is the corpus under `patterns/`. The pipeline is small.
The hard part is the pattern taxonomy and the discipline of writing
real outcomes instead of post-hoc rationalizations.

## Roles you may see in tasks

| Role | What they do |
|---|---|
| `dec-miner` | Walks a portfolio repo's `decisions/` dir, extracts DEC records with cross-domain refs |
| `pattern-taxonomist` | Assigns mined entries to one of the canonical pattern IDs |
| `outcome-tracker` | At quarter boundary, revisits 90+ day-old applications and writes the outcome field |
| `retro-writer` | Produces `patterns/YYYY-Qn-retro.md` |

These roles exist in spec ledger; not all are implemented in v0.

## Voice constraints

- No marketing words. No "leverage", "synergy", "best-in-class",
  "seamless".
- No antithetical-reversal phrasing.
- Outcome fields are written flat. "Worked", "did not work", "still
  open" plus one sentence of evidence. No hedging.
- The taxonomist must resist inventing new pattern IDs when an
  existing one fits.

## Gates (will land in spec 0002)

```bash
python -m pytest
python scripts/voice_lint.py
python scripts/validate_schemas.py
python scripts/validate_outcomes.py  # checks outcome field present for entries >= 90 days old
```

The `validate_outcomes.py` gate is the load-bearing one. Quarterly
retros that contain entries whose outcome field is still blank past
the 90-day mark do not merge.

## Out of scope

- Auto-generated pattern taxonomies. Taxonomy IDs are human-curated;
  the miner only proposes assignments.
- Cross-repo DEC modification. The miner reads other repos read-only.
- A dashboard. The artifact is the patterns/ directory plus the
  quarterly retro.
- Real-time pattern detection. Quarterly cadence is the point.
