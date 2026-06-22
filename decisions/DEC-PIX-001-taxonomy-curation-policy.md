# DEC-PIX-001 - Taxonomy curation policy

---
id: DEC-PIX-001
domain: pattern-index-governance
date: 2026-06-21
status: accepted
---

## Decision

Pattern IDs stay human-curated in `patterns/_taxonomy.yaml`.

## Reason

A pattern ID is a category claim. The miner can find cross-domain DEC records,
but it cannot prove that two applications belong to the same pattern. The
taxonomist makes that call and keeps the list small.

## Consequence

Mined entries start as `UNASSIGNED`. The validator rejects checked-in
applications whose pattern ID is not present in the taxonomy.
