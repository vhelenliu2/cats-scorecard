"""Shared calc types and helpers.

`CalcContext` carries everything a calc needs. `CalcOutput` is the calc's
contribution to a MetricRow (value + comparisons + provenance). The numeric
cores are written as pure functions so they can be unit-tested with fixtures,
independent of any live source.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..periods import PeriodContext
from ..schema import SourceEnvelope, SRC_OK, SRC_BLOCKED


@dataclass
class CalcContext:
    metric_key: str
    metric_spec: Dict[str, Any]
    goal: Dict[str, Any]
    envelopes: Dict[str, SourceEnvelope]      # source_id -> envelope
    pctx: PeriodContext
    unit: str = ""


@dataclass
class CalcOutput:
    value: Optional[float] = None
    MoM: Optional[float] = None
    QoQ: Optional[float] = None
    YoY: Optional[float] = None
    as_of: Optional[str] = None
    reason: str = ""                          # populated when value cannot be trusted
    blocked: bool = False                     # True => BLOCKED (vs REVIEW)
    manual_override: Optional[Dict[str, Any]] = None
    notes: List[str] = field(default_factory=list)


def require_ok(ctx: CalcContext, source_ids: List[str]) -> Optional[CalcOutput]:
    """Return a REVIEW/BLOCKED CalcOutput if any required source isn't usable.

    - BLOCKED source (e.g. Hex-only) => blocked output.
    - MISSING/STALE/ERROR or header-not-confirmed => review output.
    Returns None when all listed sources are OK and header-confirmed.
    """
    for sid in source_ids:
        env = ctx.envelopes.get(sid)
        if env is None:
            return CalcOutput(reason="source %r not read" % sid)
        if env.source_status == SRC_BLOCKED:
            return CalcOutput(reason="source %r blocked: %s" % (sid, env.error or ""),
                              blocked=True)
        if env.source_status != SRC_OK:
            return CalcOutput(reason="source %r status=%s: %s"
                              % (sid, env.source_status, env.error or ""))
        if env.meta.get("needs_header_confirmation"):
            return CalcOutput(reason="source %r header row not confirmed in config" % sid)
    return None


def pct_change(curr: Optional[float], prev: Optional[float]) -> Optional[float]:
    if curr is None or prev in (None, 0):
        return None
    return curr / prev - 1.0
