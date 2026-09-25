"""Google Sheets client for source pull and staging push."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class SheetsError(RuntimeError):
    pass


def _load_service_account_info() -> dict[str, Any]:
    raw = os.environ.get("GOOGLE_SHEETS_CONNECTION", "").strip()
    if raw:
        return json.loads(raw)
    path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if path:
        return json.loads(Path(path).read_text())
    local = Path(__file__).resolve().parents[1] / "secrets" / "service_account.json"
    if local.exists():
        return json.loads(local.read_text())
    raise SheetsError(
        "No Google credentials. Set GOOGLE_SHEETS_CONNECTION (Hex secret JSON) "
        "or GOOGLE_APPLICATION_CREDENTIALS."
    )


def authorize():
    try:
        import gspread
        from google.oauth2 import service_account
    except ImportError as exc:
        raise SheetsError("Install gspread and google-auth to pull/push live sheets") from exc
    info = _load_service_account_info()
    creds = service_account.Credentials.from_service_account_info(info).with_scopes(SCOPES)
    return gspread.authorize(creds), info.get("client_email")


def get_all_values(spreadsheet_id: str, tab: str | None = None, gid: int | None = None) -> tuple[str, list[list[str]]]:
    client, _ = authorize()
    book = client.open_by_key(spreadsheet_id)
    ws = None
    if tab:
        try:
            ws = book.worksheet(tab)
        except Exception:
            ws = None
    if ws is None and gid is not None:
        for candidate in book.worksheets():
            if int(candidate.id) == int(gid):
                ws = candidate
                break
    if ws is None:
        raise SheetsError(f"Worksheet not found tab={tab!r} gid={gid} in {spreadsheet_id}")
    return ws.title, ws.get_all_values()


def _header_map(headers: list[str]) -> dict[str, int]:
    return {name: i for i, name in enumerate(headers)}


def _ensure_tab(book, title: str, headers: list[str]):
    try:
        ws = book.worksheet(title)
    except Exception:
        ws = book.add_worksheet(title=title, rows=200, cols=max(len(headers), 8))
        ws.update("A1", [headers])
        return ws
    values = ws.get_all_values()
    if not values:
        ws.update("A1", [headers])
    elif values[0] != headers:
        # Keep existing headers if they are a superset; otherwise rewrite header row only.
        if set(headers) - set(values[0]):
            ws.update("A1", [headers])
    return ws


def upsert_facts(spreadsheet_id: str | None, catalog: dict, rows: list[dict], run_id: str) -> str:
    """Create or update Staging Facts / Review Queue / Run Log. Returns spreadsheet id."""
    from schema import STAGING_HEADERS, row_key

    client, email = authorize()
    title = catalog["staging"]["title"]
    if spreadsheet_id:
        book = client.open_by_key(spreadsheet_id)
    else:
        book = client.create(title)
        spreadsheet_id = book.id
        for share in catalog["staging"].get("share_with") or []:
            try:
                book.share(share, perm_type="user", role="writer", notify=False)
            except Exception as exc:
                print(f"share skipped for {share}: {exc}")
        print(f"Created staging workbook as {email}: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")

    facts = _ensure_tab(book, catalog["staging"]["facts_tab"], STAGING_HEADERS)
    review = _ensure_tab(
        book,
        catalog["staging"]["review_tab"],
        STAGING_HEADERS,
    )
    log = _ensure_tab(
        book,
        catalog["staging"]["run_log_tab"],
        ["run_id", "pulled_at", "as_of_date", "publish_ready_n", "review_n", "notes"],
    )

    existing = facts.get_all_values()
    headers = existing[0] if existing else STAGING_HEADERS
    body = existing[1:] if existing else []
    incoming_keys = {row_key(r) for r in rows}
    kept = []
    for raw in body:
        padded = raw + [""] * (len(headers) - len(raw))
        rec = {headers[i]: padded[i] for i in range(len(headers))}
        if row_key(rec) in incoming_keys:
            continue
        kept.append([rec.get(h, "") for h in STAGING_HEADERS])

    def serialize(row: dict) -> list[str]:
        out = []
        for h in STAGING_HEADERS:
            val = row.get(h)
            if val is None:
                out.append("")
            elif isinstance(val, bool):
                out.append("TRUE" if val else "FALSE")
            else:
                out.append(str(val))
        return out

    publishable = [r for r in rows if r.get("publish_ready")]
    held = [r for r in rows if not r.get("publish_ready")]
    new_body = kept + [serialize(r) for r in rows]
    facts.clear()
    facts.update("A1", [STAGING_HEADERS] + new_body)

    review.clear()
    review.update("A1", [STAGING_HEADERS] + [serialize(r) for r in held])

    pulled = rows[0]["pulled_at"] if rows else ""
    as_of = rows[0]["as_of_date"] if rows else ""
    log.append_row([run_id, pulled, as_of, len(publishable), len(held), f"n={len(rows)}"])
    return spreadsheet_id
