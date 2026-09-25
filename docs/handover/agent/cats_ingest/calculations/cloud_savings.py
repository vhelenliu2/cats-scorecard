"""Cloud Savings: YTD from the Efficiencies tracker C1.

MoM / QoQ / YoY are **intentionally blank**: Cloud Savings has no reliable as-of
date to time-phase a comparison against, so any period-over-period figure would
be misleading. These three are emitted as null by design, NOT as a missing
source. Zero savings must be preserved as 0.0, not treated as missing.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

from .base import CalcContext, CalcOutput, require_ok


def parse_money(v: Any) -> Optional[float]:
    """'$9,187,001' -> 9187001.0 ; '' / None -> None ; '$0.00' -> 0.0 (real zero)."""
    if v is None:
        return None
    s = str(v).strip()
    if s == "":
        return None
    neg = s.startswith("(") and s.endswith(")")
    s = re.sub(r"[()$,\s]", "", s)
    if s == "":
        return None
    try:
        val = float(s)
    except ValueError:
        return None
    return -val if neg else val


def cloud_from_ytd(ytd: Optional[float]) -> CalcOutput:
    """Pure core. Distinguishes 0.0 (real zero) from None (missing).

    MoM/QoQ/YoY are always None for Cloud Savings by design (see module docstring).
    """
    if ytd is None:
        return CalcOutput(reason="YTD savings (C1) unreadable")
    return CalcOutput(value=ytd, MoM=None, QoQ=None, YoY=None)


def compute(ctx: CalcContext) -> CalcOutput:
    gate = require_ok(ctx, ctx.metric_spec.get("actual_sources", []))
    if gate is not None:
        return gate

    sid = (ctx.metric_spec.get("actual_sources") or [None])[0]
    env = ctx.envelopes.get(sid)
    named = (env.meta or {}).get("named_cells", {}) if env else {}

    # The exact YTD cell key is declared in config (never guessed).
    ytd_key = ctx.metric_spec.get("ytd_named_cell") or ctx.goal.get("ytd_named_cell")
    raw = named.get(ytd_key) if ytd_key else None
    if raw is None:
        # Fall back to the checksum cell only if explicitly configured.
        chk_key = ctx.metric_spec.get("checksum_named_cell")
        raw = named.get(chk_key) if chk_key else None
        if raw is None:
            return CalcOutput(reason="Cloud Savings YTD cell %r not present in export "
                                     "named_cells; confirm C1 with Nikhil." % ytd_key)

    ytd = parse_money(raw)
    out = cloud_from_ytd(ytd)
    if out.value is not None:
        out.as_of = env.source_as_of if env else None
        out.notes.append("YTD from %s = %s (MoM/QoQ/YoY blank by design)."
                         % (ytd_key, raw))
    return out
