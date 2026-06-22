# Acceptance - v0.1 Data Report

## Commands

```bash
python -m pytest
python scripts/voice_lint.py
python scripts/validate_schemas.py
python scripts/validate_outcomes.py
python -m pattern_index validate patterns
```

## Required artifacts

- `STATUS.md`
- `docs/product-brief.md`
- `docs/system-map.md`
- `specs/0002-design/requirements.md`
- `specs/0002-design/design.md`
- `specs/0002-design/tasks.md`
- `specs/0002-design/acceptance.md`
- `pyproject.toml`
- `patterns/2026-Q2-retro.md`

## Pass condition

The tests and gates exit 0, and the report can be regenerated from the
checked-in corpus.
