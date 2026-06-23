"""Cross-domain pattern index - interactive browser.

Reads the committed patterns/ corpus directly (paths relative to this file,
no network, no secrets) and mirrors the `python -m pattern_index show` verb:
a ranked table of patterns plus a card browser over the individual
applications and their 90-day outcomes.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from pattern_index.show import (  # noqa: E402
    headline,
    load_applications,
    rank_patterns,
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
