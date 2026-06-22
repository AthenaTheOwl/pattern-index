# Product Brief

## Product

Pattern Index is a small data-report repo for tracking patterns that move
between portfolio repos. It mines DEC records, records the application as a
typed artifact, and forces an outcome check after 90 days.

## User

The primary user is a portfolio operator who reviews engineering decisions
across several repos. The user needs a quarterly view of which patterns worked,
which failed, and which are still open.

## v0.1 promise

v0.1 provides a runnable local workflow:

- Mine DEC frontmatter from a target repo into draft pattern applications.
- Validate checked-in application files against a canonical taxonomy.
- Fail when a 90-day-old application still lacks a real outcome.
- Generate a quarterly markdown report from the corpus.

## Non-goals

- No dashboard.
- No automatic taxonomy generation.
- No cross-repo writes.
- No LLM classification in the miner.

## Success signal

A reviewer can run the gates, open `patterns/2026-Q2-retro.md`, and see a
plain report of pattern use by ID and outcome.
