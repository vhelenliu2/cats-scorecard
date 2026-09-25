"""Hex-only source adapter — explicitly BLOCKED (BUILD_PLAN.md §8).

A Google service account can read shared Google Sheets but does NOT grant access
to a Hex app. Rather than screen-scrape or guess, we return a BLOCKED envelope
so the pipeline records the limitation and routes to the documented manual
fallback (e.g. `_EXP_COUNTS`) with full audit evidence.
"""

from __future__ import annotations

from typing import Any, Dict

from ..config import Config
from ..schema import SourceEnvelope, SRC_BLOCKED, utcnow_iso


def read(cfg: Config, source_id: str, spec: Dict[str, Any], url: str) -> SourceEnvelope:
    return SourceEnvelope(
        source_id=source_id, source_url=url,
        source_tab_or_query="hex_app:%s" % spec.get("hex_app", ""),
        pulled_at=utcnow_iso(), source_status=SRC_BLOCKED,
        error="Hex-only source cannot be read by a Google service account. "
              "Use the documented approved fallback with owner + evidence.",
    )
