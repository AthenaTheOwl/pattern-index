---
pattern_id: eval-as-gate
source_repo: ai-field-brief
dec_ref: DEC-MTRX-009
target_domain: field-briefing
applied_at: 2026-09-04
outcome: still-open
outcome_recorded_at: null
outcome_evidence:
  - "Still open; applied 2026-09-04 and needs the 90-day window. At landing, 6,184 cells in 17 files pass and reintroducing one drifted enum value reproduces a single named violation."
---

## Narrative

The repo added a gate that validates every matrix cell file against the cell schema, after finding 172 enum violations the schema-file check could not see.
