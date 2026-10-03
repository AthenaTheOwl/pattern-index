---
pattern_id: typed-artifact-discipline
source_repo: grid-silicon
dec_ref: DEC-GRDS-001
target_domain: energy-infrastructure
applied_at: 2026-06-20
outcome: worked
outcome_recorded_at: 2026-10-03
outcome_evidence:
  - Two monthly typed rows exist and are directly comparable on every field - grid-silicon reports/2026-05.jsonl and reports/2026-06.jsonl, same 14-key schema both months.
  - The bounded score moved with the underlying status and the movement is readable off the artifact alone - realness_score 37 to 61, status_code under_ercot_review to planning_studies_approved, mw_observed_energized 120 to 360 MW.
  - The typed gap field did the work the pattern claims for it - phantom_mw fell 1080 to 840 MW against an unchanged mw_announced of 1200, so the announced-versus-observed gap is a field rather than a reader's subtraction.
  - Five weighted evidence categories (queue_status, energization, permit, equipment, counterparty) carry per-item evidence_id, source_url and extracted_on, so a changed score is attributable to a specific new item - EV-GRDS-001..005 in May, EV-GRDS-006..010 in June.
  - SCOPE LIMIT, and it is the reason this closed as worked rather than proven in the domain - both rows are source_mode fixture. Each row's own notes field says "Live ERCOT portal fetch is deferred until API registration and terms acceptance are handled by a human." The discipline is evidenced; a result about real ERCOT large loads is not.
  - Cadence stopped after June - no monthly row exists for July, August or September 2026, so this is evidence from two runs, not a series. The blocker is the human API-registration step above, not the pattern.
---

## Narrative

The repo turned a loose grid-load question into one typed JSONL row with evidence categories, phantom MW, observed MW, and a bounded score.

## Outcome, recorded 2026-10-03

Closed as `worked` on what the pattern actually claims: typing the artifact made two
months comparable without a reader reconstructing anything, and made the
announced-versus-observed gap an explicit field. Both are visible in the two committed
rows.

Read the scope limit in `outcome_evidence` before reusing this as precedent. Both rows
run on fixtures, so this says the discipline holds, not that the realness score tracks
real ERCOT energization. Closing it `worked` on fixture evidence is a judgement call; the
alternative reading is `abandoned`, since the application has not advanced since June and
is waiting on a human to accept ERCOT's API terms. It is recorded as `worked` because
nothing about the pattern failed - what stopped was the data access upstream of it.