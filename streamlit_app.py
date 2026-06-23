"""Cross-domain pattern index - interactive browser.

Reads the committed patterns/ corpus directly (paths relative to this file,
no network, no secrets) and mirrors the `python -m pattern_index show` verb:
a ranked table of patterns plus a card browser over the individual
applications and their 90-day outcomes.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from pattern_index.frontmatter import dump_frontmatter, split_frontmatter  # noqa: E402
from pattern_index.show import (  # noqa: E402
    headline,
    load_applications,
    rank_patterns,
)
from pattern_index.validators import (  # noqa: E402
    lint_voice,
    load_taxonomy,
    validate_outcomes,
    validate_schema,
)

PATTERNS_DIR = ROOT / "patterns"

OUTCOME_BADGE = {
    "worked": "worked",
    "still-open": "still open",
    "did-not-work": "did not work",
    "abandoned": "abandoned",
}

st.set_page_config(page_title="pattern index", page_icon=":card_index:", layout="wide")

st.title("cross-domain pattern index")
st.caption(
    "patterns mined from the portfolio's decision ledgers, tagged with a "
    "90-day-later outcome. which ones actually transferred between repos?"
)

if not PATTERNS_DIR.exists():
    st.warning(f"no patterns corpus found at {PATTERNS_DIR}")
    st.stop()

apps = load_applications(PATTERNS_DIR)
if not apps:
    st.warning("the patterns corpus is empty - nothing to show.")
    st.stop()

rows = rank_patterns(apps)
repos = sorted({a.source_repo for a in apps})
closed = sum(1 for a in apps if a.outcome != "still-open")
worked = sum(1 for a in apps if a.outcome == "worked")

c1, c2, c3, c4 = st.columns(4)
c1.metric("applications", len(apps))
c2.metric("patterns", len(rows))
c3.metric("source repos", len(repos))
c4.metric("worked", f"{worked}/{closed}" if closed else "0")

st.info(headline(apps, rows))

st.subheader("patterns, ranked by reach")
st.dataframe(
    [
        {
            "pattern": r.pattern_id,
            "applications": r.applications,
            "repos": r.repos,
            "worked": r.worked,
            "still-open": r.outcomes.get("still-open", 0),
            "did-not-work": r.outcomes.get("did-not-work", 0),
            "abandoned": r.outcomes.get("abandoned", 0),
        }
        for r in rows
    ],
    hide_index=True,
    use_container_width=True,
)

st.subheader("browse applications")

outcomes = ["all"] + [o for o in OUTCOME_BADGE if any(a.outcome == o for a in apps)]
pick = st.radio("filter by outcome", outcomes, horizontal=True)

shown = apps if pick == "all" else [a for a in apps if a.outcome == pick]
shown = sorted(shown, key=lambda a: (a.pattern_id, a.source_repo))

if not shown:
    st.write("no applications match that filter.")
    st.stop()

labels = {
    f"{a.pattern_id}  <-  {a.source_repo} {a.dec_ref}": a for a in shown
}
choice = st.selectbox("pick an application", list(labels))
app = labels[choice]

left, right = st.columns([2, 1])
with left:
    st.markdown(f"### {app.pattern_id}")
    st.markdown(f"**narrative.** {app.narrative}" if app.narrative else "_no narrative._")
with right:
    st.markdown(f"**source repo.** {app.source_repo}")
    st.markdown(f"**decision.** {app.dec_ref}")
    st.markdown(f"**target domain.** {app.target_domain}")
    st.markdown(f"**applied.** {app.applied_at}")
    st.markdown(f"**outcome.** {OUTCOME_BADGE.get(app.outcome, app.outcome)}")


# ---------------------------------------------------------------------------
# interactive: validate your own pattern application against the real engine
# ---------------------------------------------------------------------------
#
# everything above reads the committed corpus. below, the user writes (or
# edits) their OWN application markdown and we run the SAME validators the CLI
# `validate` verb runs - validate_schema + validate_outcomes (the 90-day
# outcome gate) + lint_voice (the banned-word / antithesis spec check). no
# reimplementation: we stage the document into a temp patterns/ tree and call
# the real functions from pattern_index.validators.

st.divider()
st.subheader("validate your own application")
st.caption(
    "this is the actual `pattern-index validate` engine, not a lookup. write a "
    "frontmatter doc the way you'd commit it; we run validate_schema, "
    "validate_outcomes (the 90-day gate) and lint_voice against it live and tell "
    "you exactly why it passes or fails."
)

taxonomy = sorted(load_taxonomy(PATTERNS_DIR))
st.markdown(
    "**known pattern_ids** (from the committed `_taxonomy.yaml`): "
    + ", ".join(f"`{t}`" for t in taxonomy)
)

EXAMPLE_DOC = dump_frontmatter(
    {
        "pattern_id": taxonomy[0] if taxonomy else "citation-faithful-extraction",
        "source_repo": "my-new-repo",
        "dec_ref": "DEC-042",
        "target_domain": "field-briefing",
        "applied_at": "2026-03-01",
        "outcome": "worked",
        "outcome_recorded_at": "2026-06-10",
        "outcome_evidence": [
            "The downstream review confirmed the pattern held after 90 days.",
        ],
    },
    "## Narrative\n\nThe pattern transferred cleanly into the new domain and "
    "survived the outcome review.",
)

doc_text = st.text_area(
    "application markdown (frontmatter + narrative)",
    value=EXAMPLE_DOC,
    height=320,
    help="edit anything - try an unknown pattern_id, a still-open outcome older "
    "than 90 days, or a banned word like 'leverage' to watch the gate fire.",
)

as_of = st.date_input(
    "evaluate the 90-day outcome gate as of",
    value=date.today(),
    help="validate_outcomes compares applied_at against this date minus 90 days.",
)

if st.button("run the validator", type="primary"):
    metadata, _body = split_frontmatter(doc_text)
    pattern_id = str(metadata.get("pattern_id", "")).strip() or "UNKNOWN"

    # stage the document into a real patterns/ tree the validators understand:
    # <pattern_id>/applications/<file>.md plus the committed taxonomy.
    staging = Path(tempfile.mkdtemp(prefix="pattern-index-"))
    try:
        shutil.copy(PATTERNS_DIR / "_taxonomy.yaml", staging / "_taxonomy.yaml")
        app_dir = staging / pattern_id / "applications"
        app_dir.mkdir(parents=True, exist_ok=True)
        doc_path = app_dir / "candidate.md"
        doc_path.write_text(doc_text, encoding="utf-8")

        schema_errors = validate_schema(staging)
        outcome_errors = validate_outcomes(staging, as_of=as_of)
        voice_errors = lint_voice([doc_path])
    finally:
        shutil.rmtree(staging, ignore_errors=True)

    all_errors = schema_errors + outcome_errors + voice_errors
    if not all_errors:
        st.success(
            "PASS - this application would clear `pattern-index validate`: schema "
            "complete, outcome gate satisfied, voice clean."
        )
    else:
        st.error(f"FAIL - {len(all_errors)} issue(s). this would block `validate`.")

        def _show(title: str, errors: list) -> None:
            if errors:
                st.markdown(f"**{title}**")
                for err in errors:
                    st.markdown(f"- {err.message}")

        _show("schema", schema_errors)
        _show("outcome gate (90-day)", outcome_errors)
        _show("voice / spec lint", voice_errors)
