"""Read-only Google Docs adapter (for the SOTA subjective readout).

Extracts the document's plain text so the SOTA calc can scan for the most
recent dated grade. Read-only; never edits the doc.
"""

from __future__ import annotations

from typing import Any, Dict

from ..config import Config
from ..schema import SourceEnvelope, SRC_OK, SRC_MISSING, SRC_ERROR, utcnow_iso
from . import _gauth


def _flatten_text(doc: Dict[str, Any]) -> str:
    out = []
    for el in doc.get("body", {}).get("content", []):
        para = el.get("paragraph")
        if not para:
            continue
        for pe in para.get("elements", []):
            tr = pe.get("textRun")
            if tr and tr.get("content"):
                out.append(tr["content"])
    return "".join(out)


def read(cfg: Config, source_id: str, spec: Dict[str, Any], url: str) -> SourceEnvelope:
    doc_id = spec.get("document_id")
    cred_env = cfg.credentials.get("google_sheets", "GOOGLE_SHEETS_CONNECTION")
    creds = _gauth.get_readonly_credentials(cred_env)
    if creds is None:
        return SourceEnvelope(
            source_id=source_id, source_url=url, source_tab_or_query="google_doc",
            pulled_at=utcnow_iso(), source_status=SRC_MISSING,
            error="No readonly Google credentials in %r; doc not read." % cred_env,
        )
    try:
        from googleapiclient.discovery import build

        service = build("docs", "v1", credentials=creds, cache_discovery=False)
        doc = service.documents().get(documentId=doc_id).execute()
        text = _flatten_text(doc)
    except Exception as e:
        return SourceEnvelope(
            source_id=source_id, source_url=url, source_tab_or_query="google_doc",
            pulled_at=utcnow_iso(), source_status=SRC_ERROR,
            error="Doc read failed: %s" % e,
        )
    return SourceEnvelope(
        source_id=source_id, source_url=url, source_tab_or_query="google_doc",
        pulled_at=utcnow_iso(), source_status=SRC_OK,
        raw_rows=[{"text": text}], meta={"chars": len(text)},
    )
