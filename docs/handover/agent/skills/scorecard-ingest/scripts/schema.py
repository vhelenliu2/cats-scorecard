"""Staging Facts row contract."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

STAGING_HEADERS = [
    "metric_id",
    "display_name",
    "hex_display_name",
    "parent_metric_id",
    "field_kind",
    "planning_period",
    "period_type",
    "as_of_date",
    "value",
    "unit",
    "source_id",
    "source_url",
    "source_tab",
    "source_cell_hint",
    "row_matched",
    "confidence",
    "review_reason",
    "approval_status",
    "freshness_flag",
    "publish_ready",
    "pulled_at",
    "last_verified_at",
    "verified_by",
]

REVIEW_REASONS = {
    "unregistered_segment",
    "missing_column",
    "unmatched",
    "incomplete_geo",
    "value_changed",
    "late",
    "unit_suspect",
    "hex_mismatch",
}

UPSERT_KEYS = ("metric_id", "display_name", "field_kind", "period_type", "planning_period")


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def iso_date(value: date | datetime | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)[:10]


def make_row(**kwargs: Any) -> dict[str, Any]:
    row = {key: "" for key in STAGING_HEADERS}
    row.update(
        field_kind="goal",
        row_matched=False,
        confidence="review",
        approval_status="extracted_unconfirmed",
        freshness_flag="unconfirmed",
        publish_ready=False,
        pulled_at=utcnow_iso(),
        value=None,
    )
    row.update(kwargs)
    if row.get("as_of_date") and not isinstance(row["as_of_date"], str):
        row["as_of_date"] = iso_date(row["as_of_date"])
    if row.get("publish_ready") is True:
        row["publish_ready"] = True
    else:
        row["publish_ready"] = bool(row.get("publish_ready"))
    if row.get("row_matched") is True:
        row["row_matched"] = True
    else:
        row["row_matched"] = bool(row.get("row_matched"))
    return row


def row_key(row: dict[str, Any]) -> tuple:
    return tuple(str(row.get(k) or "") for k in UPSERT_KEYS)


def mark_publishable(row: dict[str, Any]) -> dict[str, Any]:
    """Clean parent extract: stage it, but do not claim owner approval."""
    row = dict(row)
    if (
        row.get("metric_id")
        and row.get("row_matched")
        and row.get("value") is not None
        and not row.get("parent_metric_id")
        and row.get("confidence") != "review"
    ):
        row["confidence"] = "high"
        row["publish_ready"] = True
        row["freshness_flag"] = "unconfirmed"
        row["approval_status"] = "extracted_unconfirmed"
    else:
        row["publish_ready"] = False
        if not row.get("confidence"):
            row["confidence"] = "review"
    return row
