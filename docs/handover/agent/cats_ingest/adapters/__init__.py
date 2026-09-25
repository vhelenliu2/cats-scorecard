"""Source adapters. Each returns a uniform SourceEnvelope and is READ-ONLY."""

from __future__ import annotations

from typing import Any, Dict

from ..config import Config
from ..schema import SourceEnvelope, SRC_ERROR
from . import gsheet, warehouse, hex_blocked, gdoc, local_export


def read_source(cfg: Config, source_id: str) -> SourceEnvelope:
    """Dispatch to the right adapter based on the source `type`."""
    spec: Dict[str, Any] = cfg.source(source_id)
    stype = spec.get("type")
    url = cfg.source_url(source_id)
    if stype == "google_sheet":
        return gsheet.read(cfg, source_id, spec, url)
    if stype == "local_export":
        return local_export.read(cfg, source_id, spec, url)
    if stype == "google_doc":
        return gdoc.read(cfg, source_id, spec, url)
    if stype == "warehouse":
        return warehouse.read(cfg, source_id, spec, url)
    if stype == "hex_app":
        return hex_blocked.read(cfg, source_id, spec, url)
    return SourceEnvelope(
        source_id=source_id,
        source_url=url,
        source_tab_or_query=str(spec.get("tab_name") or ""),
        pulled_at="",
        source_status=SRC_ERROR,
        error="Unknown source type: %r" % stype,
    )
