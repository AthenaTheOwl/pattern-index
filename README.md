# pattern-index

Fifteen pattern applications across nine repos, with thirteen closed outcome reviews.
Nine closed reviews record a transfer that held across four patterns. pattern-index
mines the `decisions/` ledgers for those transfers and then waits ninety days to find
out which ones survived contact.

## What it does

A pattern that works in one repo keeps showing up in another. `eval-as-gate` was a
RAG habit before it became a procurement one; typed-artifact discipline went the other
way. None of that gets written down at the time, so the same lesson gets re-learned
per repo and the control plane upstream has no record of what actually transferred.

pattern-index reads the DEC records already sitting in each repo's `decisions/`
directory, finds the ones that borrow a principle from another domain or cite a prior
decision from another repo, and files each as a pattern application. Then it adds the
field nobody writes upfront: the outcome, ninety days later. A pattern with two
applications and no closed reviews is a hunch. A pattern that transferred twice and
held both times is a rule. The mining is static analysis of DEC frontmatter — no model
in the loop for that step.

The artifact is `patterns/<pattern_id>/applications/<case>.md` plus one quarterly
`pattern_index_retro.md`. The cadence is quarterly because ninety days is the point.

## Try it

One command, no setup. It reads the committed corpus and ranks it:

```bash
python -m pattern_index show
```

```
cross-domain pattern index
15 applications  -  5 patterns  -  9 source repos  -  13 closed reviews

pattern                      apps repos worked  outcomes
--------------------------------------------------------
eval-as-gate                    5     4      3  worked 3, still-open 2
typed-artifact-discipline       4     4      3  worked 3, did-not-work 1
voice-lint-as-spec-check        2     2      2  worked 2
citation-faithful-extraction    2     2      1  worked 1, did-not-work 1
dec-then-implement              2     2      0  abandoned 2
```

The list is ranked by how many applications each pattern carries, then by how many
worked; the `repos` column shows reach. The `outcomes` column records the outcome: of
thirteen closed reviews, nine record a transfer that held. Those are corpus
observations backed by the evidence lines in each application; they are not
independent proof of every downstream domain claim.

For a date-filtered outcome view, use
`python -m pattern_index show --as-of 2026-06-30`. Applications dated later are
excluded; a closed outcome recorded after the cutoff, or without an observation
date, appears as `still-open`. Default `show` keeps its current-corpus behavior.

This prevents later outcome observations from entering an earlier summary. It
filters the current files; it cannot recover deleted applications or prior edits.
Use a retained Git revision for an actual historical corpus snapshot.

## live demo

A streamlit card browser over the same committed corpus: a ranked pattern table plus a
per-application card (source repo, decision, target domain, 90-day outcome, narrative).

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Deploy on Streamlit Community Cloud from repo `AthenaTheOwl/pattern-index`,
branch `main`, main file `streamlit_app.py`.

<!-- live-url: -->

## How it connects

The corpus is mined out of the sibling ledgers and fed back to the control plane:

- [procurement-negotiation-lab](https://github.com/AthenaTheOwl/procurement-negotiation-lab)
  — the richest DEC ledger, and the first one worth mining.
- [supplier-risk-rag-agent](https://github.com/AthenaTheOwl/supplier-risk-rag-agent)
  — where the eval-discipline patterns started before they crossed over.
- [ai-field-brief](https://github.com/AthenaTheOwl/ai-field-brief)
  — origin of the voice-and-traceability patterns.
- Any CDCP / control-plane app consumes the mined corpus as principle-to-application
  data to learn from.

## Run it in full

All five verbs run against the committed `patterns/` corpus.

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

# list still-open applications due for 90-day outcome review
python -m pattern_index worklist --as-of 2026-07-05 --horizon-days 30
```

A pattern application is, concretely, a DEC record in some repo's `decisions/`
directory that either names a principle from a different domain than its host repo, or
cites a prior DEC record from another repo as its origin. Both shapes are detectable
from the frontmatter.

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
  src/pattern_index/     # mine / retro / validate / show / worklist
  streamlit_app.py       # interactive card browser
```

## License

MIT. See [LICENSE](LICENSE).
