# Requirements - v0.1 Data Report

Brand prefix: PIX.

## Functional requirements

- **R-PIX-013** - The repo SHALL expose a Python CLI through
  `python -m pattern_index`.
- **R-PIX-014** - The CLI SHALL support `mine`, `validate`, and `retro`
  subcommands.
- **R-PIX-015** - The miner SHALL write draft applications with
  `pattern_id: UNASSIGNED`.
- **R-PIX-016** - Validation SHALL reject checked-in applications whose
  `pattern_id` is absent from `patterns/_taxonomy.yaml`.
- **R-PIX-017** - Validation SHALL reject applications older than 90 days when
  they still carry `outcome: still-open`.
- **R-PIX-018** - The repo SHALL include one checked-in quarterly retro report.

## Packaging requirements

- **R-PIX-019** - `pyproject.toml` SHALL declare dev tools under
  `[dependency-groups]`.
- **R-PIX-020** - `pyproject.toml` SHALL set `[tool.uv] package = true`.

## Status requirements

- **R-PIX-021** - `STATUS.md` SHALL contain exact H2 headings for current
  state, known limits, and next feature queue.
