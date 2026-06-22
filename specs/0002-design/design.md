# Design - v0.1 Data Report

## CLI shape

```
python -m pattern_index mine --repo <repo> --out <patterns_dir>
python -m pattern_index validate patterns
python -m pattern_index retro --quarter 2026-Q2 --out patterns/2026-Q2-retro.md
```

The CLI wraps small library functions so tests can exercise the behavior
without shelling out.

## Frontmatter parser

The repo uses a tiny YAML-frontmatter subset parser. It supports scalar fields
and flat lists, which covers the DEC and pattern application files used in v0.1.
This keeps the gates runnable before dependency sync. The package metadata still
declares `pyyaml` and `jsonschema` for later expansion.

## Mining flow

1. Walk `<repo>/decisions/*.md`.
2. Parse frontmatter.
3. Treat a DEC as cross-domain when a reference points at another repo or when
   the DEC domain differs from the repo primary domain.
4. Write the result to `UNASSIGNED/applications/<source_repo>-<dec_id>.md`.

## Validation flow

1. Load canonical pattern IDs from `patterns/_taxonomy.yaml`.
2. Read each `patterns/*/applications/*.md` file except `UNASSIGNED`.
3. Check required fields and enum values.
4. Check the folder name matches `pattern_id`.
5. Enforce the 90-day outcome rule.

## Retro flow

The retro writer reads the same application files, counts applications by
pattern ID and outcome, then writes a short markdown report. Human editing can
improve the narrative later, but the generated artifact is useful on its own.
