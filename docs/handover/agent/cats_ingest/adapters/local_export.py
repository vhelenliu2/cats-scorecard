"""Read-only local export adapter.

Reads a JSON file that is a faithful transcription of an approved source sheet
(e.g. a PDF/CSV export a human downloaded read-only). This exists so the exact
same normalize -> validate -> calculate -> stage pipeline can run without live
Google credentials, while preserving every guardrail:

  * It NEVER writes anything (open in read mode only).
  * It returns the same :class:`SourceEnvelope` shape as the live gsheet adapter,
    so the calc layer is source-agnostic.
  * `source_url` still points at the real (read-only, deny-listed) source id for
    provenance, but the bytes come from the local export file.

Config spec (per source):
    type: local_export
    export_file: "source_exports/<file>.json"
    spreadsheet_id / gid  (optional, for provenance URL only)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from ..config import Config
from ..schema import SourceEnvelope, SRC_OK, SRC_MISSING, SRC_ERROR, utcnow_iso

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def read(cfg: Config, source_id: str, spec: Dict[str, Any], url: str) -> SourceEnvelope:
    rel = spec.get("export_file")
    tab_desc = spec.get("tab_name") or (rel or "")
    if not rel:
        return SourceEnvelope(
            source_id=source_id, source_url=url, source_tab_or_query=tab_desc,
            pulled_at=utcnow_iso(), source_status=SRC_MISSING,
            error="local_export source has no export_file configured.",
        )

    path = REPO_ROOT / rel
    if not path.exists():
        return SourceEnvelope(
            source_id=source_id, source_url=url, source_tab_or_query=tab_desc,
            pulled_at=utcnow_iso(), source_status=SRC_MISSING,
            error="export_file not found: %s" % path,
        )

    try:
        # read-only: parse the transcribed export
        data = json.loads(path.read_text())
    except Exception as e:  # malformed export
        return SourceEnvelope(
            source_id=source_id, source_url=url, source_tab_or_query=tab_desc,
            pulled_at=utcnow_iso(), source_status=SRC_ERROR,
            error="Failed to parse export %s: %s" % (path, e),
        )

    rows: List[Dict[str, Any]] = list(data.get("rows", []))
    meta: Dict[str, Any] = {
        "raw_grid_rows": len(rows),
        "export_file": str(rel),
    }
    for k in ("named_cells", "columns", "monthly_totals", "summary"):
        if k in data:
            meta[k] = data[k]

    return SourceEnvelope(
        source_id=source_id, source_url=url, source_tab_or_query=tab_desc,
        pulled_at=utcnow_iso(), source_status=SRC_OK,
        source_as_of=data.get("source_as_of"), raw_rows=rows, meta=meta,
    )
