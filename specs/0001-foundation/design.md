# Design — Foundation

## Shape

Two pipelines, one shared schema. Quarterly cadence.

```
       +----------------------+
       |  pattern taxonomy    |   patterns/_taxonomy.yaml
       +----------------------+
              ^      ^
              |      |
+-------------+      +-------------+
|  miner pipeline    |   retro writer       |
|  (per-repo, monthly|   (cross-repo,       |
|  if you want)      |   quarterly)         |
+--------------------+----------------------+
              |                |
       patterns/<id>/applications/*.md
```

## Mining algorithm

The miner is deliberately dumb. No LLM. Static analysis of DEC
markdown frontmatter:

1. Walk `<target_repo>/decisions/*.md`.
2. Parse YAML frontmatter from each file. Expect at minimum:
   `id`, `domain`, optional `references`.
3. A DEC is a cross-domain candidate if:
   - `references` contains an entry of shape `<other-repo>#DEC-XXX`,
     OR
   - `domain` differs from the host repo's primary domain (which the
     miner reads from `<target_repo>/AGENTS.md` or a fallback config).
4. For each candidate, emit a draft
   `patterns/UNASSIGNED/applications/<source_repo>-<dec_id>.md` with
   `pattern_id: UNASSIGNED` and `outcome: still-open`.
5. A human taxonomist promotes UNASSIGNED entries to a real
   `pattern_id` by moving the file. The miner never invents IDs.

## Why the miner never assigns IDs

A pattern-id assignment is a load-bearing categorical claim. If the
miner gets it wrong, downstream quarterly retros silently report
nonsense. Keeping assignment human-only means the corpus stays
trustworthy at the cost of friction. That is the right trade for a
quarterly artifact.

## Outcome backfill

Quarterly, the retro writer:

1. Reads all `patterns/*/applications/*.md` with `applied_at` >= 90
   days ago and `outcome: still-open`.
2. Emits a "needs outcome" worklist file.
3. Operator (human) fills outcome + evidence for each.
4. Validator confirms no `still-open` entries remain past the 90-day
   cliff; retro merges.

## Schema sketch

```yaml
# patterns/eval-as-gate/applications/supplier-risk-rag-agent-DEC-014.md
---
pattern_id: eval-as-gate
source_repo: supplier-risk-rag-agent
dec_ref: DEC-014
target_domain: rag-eval-discipline
applied_at: 2026-03-12
outcome: worked
outcome_recorded_at: 2026-06-14
outcome_evidence:
  - "CI gate caught faithfulness regression on PR 142, blocked merge."
  - "Three subsequent PRs added cases to the suite without LLM-judge."
---

## Narrative
One paragraph the human writes describing the application in flat
prose.
```

## Dependencies

- `pyyaml` for frontmatter parsing.
- `jsonschema` for validation.
- `pathlib` and `re` for repo walks. No graph DB. No LLM. No web
  framework.

## What is deliberately NOT in v0

- Auto-detection of pattern similarity via embeddings.
- A web UI to browse the patterns/ corpus.
- Cross-repo PR generation when a pattern is detected.
- Real-time mining hooks. Manual invocation per repo.
