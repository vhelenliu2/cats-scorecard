"""Ads SOTA ML: the right-most filled quarter column of the S-pillar sheet row.

MoM/QoQ/YoY blank unless comparable historical grades exist. Pacing is NOT
computed unless an approved grade->rank mapping is configured (handled in
goals.py -> REVIEW when missing). agent_build_plan.md §4.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any, List, Optional, Tuple

from ..schema import SRC_OK
from .base import CalcContext, CalcOutput

# Matches e.g. "Sep 2026 ... grade: B+" style lines. Conservative: needs a date
# token and an explicit grade token near each other.
_DATE_RE = re.compile(
    r"(\d{4}-\d{2}-\d{2})|((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})",
    re.IGNORECASE,
)
_GRADE_RE = re.compile(r"\bgrade\b[^A-Fa-f]{0,12}([A-F][+-]?)(?![A-Za-z0-9])", re.IGNORECASE)
_MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def _parse_date(tok: str) -> Optional[date]:
    tok = tok.strip()
    try:
        return date.fromisoformat(tok)
    except ValueError:
        pass
    parts = tok.replace(".", "").split()
    if len(parts) == 2 and parts[0][:3].lower() in _MONTHS:
        return date(int(parts[1]), _MONTHS[parts[0][:3].lower()], 1)
    return None


def latest_dated_grade(text: str) -> Optional[Tuple[date, str]]:
    """Pure core. Returns (date, grade) for the most recent dated grade, or None."""
    best: Optional[Tuple[date, str]] = None
    for line in text.splitlines():
        gm = _GRADE_RE.search(line)
        dm = _DATE_RE.search(line)
        if not (gm and dm):
            continue
        d = _parse_date(dm.group(0))
        if d is None:
            continue
        if best is None or d > best[0]:
            best = (d, gm.group(1).upper())
    return best


_GRADE_PERIOD_ORDER = ("q4_2026", "q3_2026_trending", "q3_2026", "q2_2026", "q1_2026")


def latest_structured_grade(grades: dict) -> Optional[Tuple[str, str]]:
    """Return (period_key, grade) for the right-most filled quarter column.

    Excludes the forward-looking `goal_2026` cell — that is the target, not an actual.
    """
    for key in _GRADE_PERIOD_ORDER:
        val = grades.get(key)
        if val and str(val).strip():
            return key, str(val).strip()
    return None


def compute(ctx: CalcContext) -> CalcOutput:
    ids = ctx.metric_spec.get("actual_sources", [])
    env = ctx.envelopes.get(ids[0]) if ids else None
    if env is None or env.source_status != SRC_OK:
        return CalcOutput(reason="S-pillar sheet not read: %s"
                          % (env.error if env else "no source"))

    # Preferred: structured grade cells transcribed from the S-pillar sheet row.
    grades = ((env.meta or {}).get("named_cells", {}) or {}).get("sota_grades", {})
    if grades:
        found = latest_structured_grade(grades)
        if not found:
            return CalcOutput(reason="no actual SOTA grade in the S-pillar sheet row; "
                                     "confirm the quarter column is filled in")
        period_key, grade = found
        goal_grade = str(grades.get("goal_2026") or "").strip() or None
        return CalcOutput(
            value=None, as_of=env.source_as_of,
            reason="grade=%s (categorical); pace needs approved grade->rank map" % grade,
            notes=["latest SOTA grade %s (%s); 2026 goal grade %s"
                   % (grade, period_key, goal_grade or "—")],
        )

    # Fallback: scan free-text subjective readout for the most recent dated grade.
    text = env.raw_rows[0].get("text", "") if env.raw_rows else ""
    found = latest_dated_grade(text)
    if not found:
        return CalcOutput(reason="no dated grade found in subjective readout; "
                                 "confirm a readout is posted")
    d, grade = found
    return CalcOutput(value=None, as_of=d.isoformat(),
                      reason="grade=%s (categorical); pace needs approved grade map" % grade,
                      notes=["latest grade %s as of %s" % (grade, d.isoformat())])
