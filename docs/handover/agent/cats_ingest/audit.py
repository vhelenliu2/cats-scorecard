"""Run audit / provenance records.

Every run emits a Run Audit (one row per source pull) and preserves raw rows so
a partial source failure is always visible and never silently produces a
complete-looking dashboard row (BUILD_PLAN.md §7 last paragraph).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .schema import SourceEnvelope, ValidationFinding, utcnow_iso


@dataclass
class AuditLog:
    run_id: str
    as_of: str
    write_mode: str
    started_at: str = field(default_factory=utcnow_iso)
    source_rows: List[Dict[str, Any]] = field(default_factory=list)
    findings: List[Dict[str, Any]] = field(default_factory=list)
    raw_rows: List[Dict[str, Any]] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def record_source(self, metric: str, env: SourceEnvelope) -> None:
        self.source_rows.append({
            "run_id": self.run_id,
            "metric": metric,
            "source_id": env.source_id,
            "source_status": env.source_status,
            "source_as_of": env.source_as_of,
            "pulled_at": env.pulled_at,
            "source_url": env.source_url,
            "source_tab_or_query": env.source_tab_or_query,
            "n_raw_rows": len(env.raw_rows),
            "error": env.error or "",
        })
        # Preserve a bounded sample of raw rows for provenance.
        for r in env.raw_rows[:200]:
            self.raw_rows.append({"run_id": self.run_id, "metric": metric,
                                  "source_id": env.source_id, **_stringify(r)})

    def record_findings(self, findings: List[ValidationFinding]) -> None:
        for x in findings:
            self.findings.append({
                "run_id": self.run_id, "metric": x.metric,
                "check": x.check, "status": x.status, "detail": x.detail,
            })


def _stringify(row: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    for k, v in row.items():
        if isinstance(v, (list, dict)):
            out[str(k)] = str(v)[:500]
        else:
            out[str(k)] = v
    return out
