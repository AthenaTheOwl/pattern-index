---
pattern_id: typed-artifact-discipline
source_repo: ai-field-brief
dec_ref: DEC-006
target_domain: field-briefing
applied_at: 2026-04-12
outcome: did-not-work
outcome_recorded_at: 2026-09-04
outcome_evidence:
  - "Did not work as applied: nothing validated the typed brief file, so 172 schema violations accrued across eight issues (2026-W24 to W34) and three issues shipped without required Top-signal fields, until validate_matrix_cells and validate_brief_fields landed 2026-09-04 (DEC-MTRX-009, DEC-PUB-013)."
---

## Narrative

The repo used a typed brief file to keep source, claim, and action fields separate.
