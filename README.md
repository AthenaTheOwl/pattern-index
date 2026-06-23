# Cross-Domain Pattern Index

A quarterly mining pass over the user's `decisions/` ledgers across
the portfolio that extracts cross-domain pattern applications
(procurement-to-AI-build and back), tags each with an outcome 90 days
later, and writes a quarterly retro.

## What this is

The previous framing was a "procurement pattern library" with
curated entries written upfront. That collapses into either dead
documentation or LLM-generated taxonomy soup. This repo instead
*mines* existing DEC ledgers for already-implemented pattern
applications, then adds the one field nobody writes upfront: outcome,
90 days later.

The artifact is `patterns/<pattern_id>/applications/<case>.md` plus
one quarterly `pattern_index_retro.md`. The intended cadence is
quarterly.

## Why this exists

The user runs ~20 active repos. Patterns that worked in
`procurement-negotiation-lab` keep showing up later in
`supplier-risk-rag-agent` or `ai-field-brief`. The reverse also
happens — eval-discipline patterns from RAG land in procurement. None
of this is being typed today. Untyped cross-domain transfer means the
CDCP control-plane has no principle-to-application data to learn
from.

This repo is the mining pass that fixes that.

## Status


v0.1 shipped — runnable, minimal. The first real deliverable is in place; the next passes deepen it (more scenarios, real-data backfill). The entry command `python -m pattern_index validate` runs. See `specs/0002-design/` for the v0.1 scope and `STATUS.md` (where present) for the current state and next-feature queue.

## How to run

All four verbs run today against the committed `patterns/` corpus.

```bash
# ranked, readable summary of the committed corpus (read-only, no args)
python -m pattern_index show

# validate the corpus schema + 90-day outcome rules
python -m pattern_index validate

# mine a sibling repo's decisions/ for cross-domain candidates
python -m pattern_index mine \
  --repo ../procurement-negotiation-lab \
  --out patterns/

# write a quarterly retro
python -m pattern_index retro \
  --quarter 2026-Q3 \
  --out patterns/2026-Q3-retro.md
```

`show` prints which patterns reach the most repos and which ones actually
held on their 90-day outcome review.

## live demo

A streamlit card browser over the same committed corpus: a ranked pattern
table plus a per-application card (source repo, decision, target domain,
90-day outcome, narrative).

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Deploy on Streamlit Community Cloud from repo `AthenaTheOwl/pattern-index`,
branch `main`, main file `streamlit_app.py`.

<!-- live-url: -->


## Layout

```
pattern-index/
  README.md
  LICENSE
  AGENTS.md
  .gitignore
  specs/
    0001-foundation/
      requirements.md
      design.md
      tasks.md
      acceptance.md
  docs/
    first-pr.md
  patterns/              # mined entries land here
  src/pattern_index/     # mine / retro / validate / show
  streamlit_app.py       # interactive card browser
```

## What gets mined

A "pattern application" is, concretely, a DEC record in some repo's
`decisions/` directory that:

1. Names a principle drawn from a different domain than the host
   repo's primary domain, OR
2. References a prior DEC record from a different repo as its origin.

Both shapes are detectable by static analysis of DEC frontmatter, no
LLM required for the mining step.

## Compounds with

- `procurement-negotiation-lab` (richest DEC ledger to mine first)
- `supplier-risk-rag-agent` (eval-discipline patterns originated here)
- `ai-field-brief` (voice-and-traceability patterns)
- Any CDCP / control-plane app (consumes the mined corpus as input)

## License

MIT. See [LICENSE](LICENSE).
