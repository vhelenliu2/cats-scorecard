"""Read-only warehouse adapter (interface + safe default).

The MVP does not hard-wire a specific warehouse client. It executes the SQL
referenced by `query_ref` through a runtime-provided read-only runner if one is
registered; otherwise it returns MISSING so the calc emits REVIEW/BLOCKED.

A runner is any callable(sql: str) -> list[dict]. Register it with
`register_runner(...)` at runtime (e.g. wrapping agent_redd_ds.query.run_query
in read-only mode). We NEVER run DML/DDL; only the .sql files under sql/.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ..config import Config
from ..schema import SourceEnvelope, SRC_OK, SRC_MISSING, SRC_ERROR, utcnow_iso

_RUNNER: Optional[Callable[[str], List[Dict[str, Any]]]] = None

# Statements we refuse to execute (defense in depth; sources are read-only).
_FORBIDDEN_SQL = ("insert ", "update ", "delete ", "drop ", "alter ",
                  "create ", "merge ", "truncate ", "grant ", "replace ")


def register_runner(runner: Callable[[str], List[Dict[str, Any]]]) -> None:
    global _RUNNER
    _RUNNER = runner


def _assert_readonly_sql(sql: str) -> None:
    low = " " + sql.lower().replace("\n", " ")
    for kw in _FORBIDDEN_SQL:
        if (" " + kw) in low:
            raise ValueError("Refusing non-read-only SQL (contains %r)." % kw.strip())


def read(cfg: Config, source_id: str, spec: Dict[str, Any], url: str) -> SourceEnvelope:
    qref = spec.get("query_ref", "")
    if _RUNNER is None:
        return SourceEnvelope(
            source_id=source_id, source_url=url, source_tab_or_query=qref,
            pulled_at=utcnow_iso(), source_status=SRC_MISSING,
            error="No warehouse runner registered; query not executed.",
        )
    sql_path = Path(__file__).resolve().parent.parent.parent / qref
    if not sql_path.exists():
        return SourceEnvelope(
            source_id=source_id, source_url=url, source_tab_or_query=qref,
            pulled_at=utcnow_iso(), source_status=SRC_MISSING,
            error="SQL file not found: %s" % qref,
        )
    sql = sql_path.read_text()
    try:
        _assert_readonly_sql(sql)
        rows = _RUNNER(sql)
    except Exception as e:
        return SourceEnvelope(
            source_id=source_id, source_url=url, source_tab_or_query=qref,
            pulled_at=utcnow_iso(), source_status=SRC_ERROR,
            error="Warehouse read failed: %s" % e,
        )
    return SourceEnvelope(
        source_id=source_id, source_url=url, source_tab_or_query=qref,
        pulled_at=utcnow_iso(), source_status=SRC_OK, raw_rows=list(rows),
    )
