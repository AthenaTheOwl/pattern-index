# Requirements — Foundation

Brand prefix: PIX (pattern-index).

## Functional requirements

- **R-PIX-001** — The repo SHALL define a typed schema
  `schemas/pattern_application.schema.json` covering: pattern_id,
  source_repo, dec_ref, target_domain, applied_at, outcome,
  outcome_recorded_at, outcome_evidence.
- **R-PIX-002** — The repo SHALL maintain `patterns/_taxonomy.yaml`
  as the single source of truth for valid `pattern_id` values. Mined
  entries assigned to an absent `pattern_id` SHALL fail validation.
- **R-PIX-003** — The DEC-miner SHALL read a target repo's
  `decisions/` directory and emit candidate pattern applications by
  detecting cross-domain references in DEC frontmatter.
- **R-PIX-004** — A candidate is "cross-domain" iff its DEC
  frontmatter cites a prior DEC in a different repo, OR its `domain`
  field differs from the host repo's primary domain.

## Artifact requirements

- **R-PIX-005** — Each mined entry SHALL be written to
  `patterns/<pattern_id>/applications/<source_repo>-<dec_id>.md`.
- **R-PIX-006** — The outcome field SHALL accept one of: `worked`,
  `did-not-work`, `still-open`, `abandoned`. No other values.
- **R-PIX-007** — Outcome SHALL be `still-open` until at least 90
  days after `applied_at`, after which the outcome must be revisited
  before the next quarterly retro merges.

## Retro requirements

- **R-PIX-008** — The retro writer SHALL produce
  `patterns/YYYY-Qn-retro.md` summarizing: count by pattern_id, count
  by outcome, two-paragraph qualitative narrative, list of newly
  detected pattern IDs proposed for the taxonomy.

## Voice and gate requirements

- **R-PIX-009** — All entries and retros SHALL pass
  `scripts/voice_lint.py`.
- **R-PIX-010** — `scripts/validate_outcomes.py` SHALL fail the build
  if any entry older than 90 days carries `outcome: still-open` without
  an explicit `outcome_recorded_at` justification.
- **R-PIX-011** — `scripts/validate_schemas.py` SHALL validate every
  entry against the canonical schema and reject unknown pattern IDs.
- **R-PIX-012** — The repo SHALL include a `decisions/` directory of
  its own, dogfooding the same DEC discipline it mines elsewhere.
