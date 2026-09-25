"""Normalized internal schema, source envelopes, and output rows.

Every adapter returns a :class:`SourceEnvelope`. Adapters/calcs produce
:class:`NormalizedRecord`s. The pipeline emits one :class:`MetricRow` per
metric plus a set of :class:`ValidationFinding`s.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Sentinel used in config for values that must be confirmed by an owner.
CONFIRM = "CONFIRM"

# ---- status vocabularies -----------------------------------------------------
# Source-level status (freshness / availability of an upstream source).
SRC_OK = "OK"
SRC_MISSING = "MISSING"
SRC_STALE = "STALE"
SRC_BLOCKED = "BLOCKED"      # e.g. Hex-only source a service account cannot read
SRC_ERROR = "ERROR"

# Metric value status (goal_binary colour, runbook §"Status colours").
VAL_GREEN = "Green"
VAL_YELLOW = "Yellow"       # a HEALTHY band (e.g. shopping_pace 70-85%), not a flag
VAL_RED = "Red"
VAL_GREY = "Grey"           # no official / computable target

# Validation status (is this row publishable to staging?).
V_PASS = "PASS"
V_REVIEW = "REVIEW"         # not publishable: needs a human decision
V_BLOCKED = "BLOCKED"       # not publishable: a hard gate failed


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class SourceEnvelope:
    """Uniform result of a single source read (BUILD_PLAN.md §6)."""

    source_id: str
    source_url: str
    source_tab_or_query: str
    pulled_at: str
    source_status: str                       # one of SRC_*
    source_as_of: Optional[str] = None       # freshest reporting date in the data
    raw_rows: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    def ok(self) -> bool:
        return self.source_status == SRC_OK


@dataclass
class NormalizedRecord:
    metric: str
    period: str                              # e.g. "2026-08" or "Q3 2026"
    value: Optional[float]
    unit: str
    source_id: str
    source_as_of: Optional[str] = None
    manual_override: Optional[Dict[str, Any]] = None


@dataclass
class ValidationFinding:
    metric: str
    check: str
    status: str                              # PASS | REVIEW | BLOCKED
    detail: str = ""

    def failed(self) -> bool:
        return self.status in (V_REVIEW, V_BLOCKED)


@dataclass
class MetricRow:
    """One staging output row. Mirrors BUILD_PLAN.md §2 required columns."""

    metric: str
    value: Optional[float] = None
    MoM: Optional[float] = None
    QoQ: Optional[float] = None
    YoY: Optional[float] = None
    current_quarter_goal: Optional[float] = None
    QTD_goal: Optional[float] = None
    pacing_to_QTD_goal: Optional[float] = None
    goal_2026: Optional[float] = None
    # auditability extras
    unit: str = ""
    as_of: Optional[str] = None
    quarter: Optional[str] = None
    status: str = VAL_GREY                    # Green/Red/Grey
    source_status: str = SRC_MISSING
    source_url: str = ""
    source_tab: str = ""
    validation_status: str = V_REVIEW         # PASS/REVIEW/BLOCKED
    review_reason: str = ""
    run_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Canonical column order for the staging "output" tab.
OUTPUT_COLUMNS: List[str] = [
    "run_id",
    "metric",
    "value",
    "unit",
    "MoM",
    "QoQ",
    "YoY",
    "current_quarter_goal",
    "QTD_goal",
    "pacing_to_QTD_goal",
    "goal_2026",
    "quarter",
    "as_of",
    "status",
    "source_status",
    "validation_status",
    "review_reason",
    "source_url",
    "source_tab",
]
