---
pattern_id: voice-lint-as-spec-check
source_repo: ai-field-brief
dec_ref: DEC-009
target_domain: editorial-quality
applied_at: 2026-05-16
outcome: worked
outcome_recorded_at: 2026-09-04
outcome_evidence:
  - "Worked: the voice gate ran in CI on every push since 2026-05-16, every issue 2026-W22 through W36 shipped lint-clean, and on 2026-09-04 it caught 20 WARN and 1 FAIL on the W35 draft before publish."
---

## Narrative

The repo made voice checks part of the spec gate for generated briefs.
