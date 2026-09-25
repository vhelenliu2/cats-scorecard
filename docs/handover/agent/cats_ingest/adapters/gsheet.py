"""Read-only Google Sheets adapter (gspread).

Reads a worksheet's values with retry/backoff. Never mutates the sheet.
If credentials or the confirmed tab/header are missing, returns a MISSING
envelope so the calc layer emits REVIEW rather than fabricating data.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

from .. import safety
from ..config import Config, is_confirmed
from ..schema import (
    SourceEnvelope,
    SRC_OK,
    SRC_MISSING,
    SRC_ERROR,
    utcnow_iso,
)
from . import _gauth


def _with_backoff(fn, attempts: int = 3, base: float = 0.5):
    last = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:  # transient read errors
            last = e
            time.sleep(base * (2 ** i))
    raise last


def read(cfg: Config, source_id: str, spec: Dict[str, Any], url: str) -> SourceEnvelope:
    sid = spec.get("spreadsheet_id")
    tab = spec.get("tab_name")
    gid = spec.get("gid")
    tab_desc = tab or ("gid=%s" % gid if gid is not None else "")

    # Never allow this adapter to be pointed at a write; it is read-only anyway,
    # but assert the id is a legitimate (forbidden-to-write) source.
    cred_env = cfg.credentials.get("google_sheets", "GOOGLE_SHEETS_CONNECTION")
    client = _gauth.get_readonly_client(cred_env)
    if client is None:
        return SourceEnvelope(
            source_id=source_id, source_url=url, source_tab_or_query=tab_desc,
            pulled_at=utcnow_iso(), source_status=SRC_MISSING,
            error="No readonly Google credentials in %r; source not read." % cred_env,
            meta={"credential_ref": cred_env},
        )

    try:
        def _open():
            sh = client.open_by_key(sid)
            if tab is not None:
                return sh.worksheet(tab)
            if gid is not None:
                for ws in sh.worksheets():
                    if str(ws.id) == str(gid):
                        return ws
            return sh.sheet1

        ws = _with_backoff(_open)
        values: List[List[str]] = _with_backoff(ws.get_all_values)
    except Exception as e:
        return SourceEnvelope(
            source_id=source_id, source_url=url, source_tab_or_query=tab_desc,
            pulled_at=utcnow_iso(), source_status=SRC_ERROR,
            error="Read failed: %s" % e,
        )

    header_row = spec.get("header_row")
    rows: List[Dict[str, Any]] = []
    meta: Dict[str, Any] = {"raw_grid_rows": len(values)}
    if is_confirmed(header_row) and values:
        hr = int(header_row) - 1
        headers = values[hr] if 0 <= hr < len(values) else []
        for r in values[hr + 1:]:
            rows.append({headers[i] if i < len(headers) else "col%d" % i: c
                         for i, c in enumerate(r)})
    else:
        # Header row not confirmed: return the raw grid so a human can confirm,
        # but flag that structured parsing is not authorized yet.
        meta["needs_header_confirmation"] = True
        meta["raw_grid"] = values[:50]

    return SourceEnvelope(
        source_id=source_id, source_url=url, source_tab_or_query=tab_desc,
        pulled_at=utcnow_iso(), source_status=SRC_OK,
        source_as_of=None, raw_rows=rows, meta=meta,
    )
