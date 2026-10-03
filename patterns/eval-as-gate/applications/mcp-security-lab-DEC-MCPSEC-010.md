---
pattern_id: eval-as-gate
source_repo: mcp-security-lab
dec_ref: DEC-MCPSEC-010
target_domain: mcp-security
applied_at: 2026-07-05
outcome: worked
outcome_recorded_at: 2026-10-03
outcome_evidence:
  - The scorecard survived the window and is still committed and enforced - mcp-security-lab reports/eval-scorecard.json plus tests/test_eval_scorecard.py, 6 tests passing.
  - Accuracy improved rather than drifting. DEC-MCPSEC-010 recorded overall precision 1.00 and recall 0.92 with two named recall gaps; the current scorecard reads precision 1.0, recall 1.0, f1 1.0 with tp 26, fp 0, fn 0, tn 74, so both gaps were closed.
  - The mechanism the pattern claims is the one that held - DEC-MCPSEC-010 argued that a rule edit trading recall for noise should surface as a failing test with a visible precision/recall delta rather than silent drift, and the pinned test is what carries that.
  - Scope - one hand-labelled 100-item real-config corpus for this scanner. It evidences the gate holding on that corpus, not accuracy on configs outside it.
---

## Narrative

The repo promoted scanner accuracy from synthetic fixtures to a committed real-config scorecard with pinned precision and recall.

## Outcome, recorded 2026-10-03

Closed as `worked` at the 90-day review. The scorecard is still in the repo, the test
that pins it still passes, and the two recall gaps the DEC named have since been closed
with no loss of precision. Read the scope line before reusing it as precedent: the
evidence is one hand-labelled corpus, so it says the gate holds, not that the scanner
generalises.