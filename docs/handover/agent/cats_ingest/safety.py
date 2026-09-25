"""Safety guardrails: staging-only, read-only sources, never touch the dashboard.

This module is the hard boundary the whole skill is built around. Two invariants:

  1. Source reads are READ-ONLY. Adapters request read-only OAuth scopes and the
     skill never calls a mutating Sheets/Docs/warehouse API.
  2. Writes go ONLY to an isolated staging target that is NOT any known
     dashboard or source. :func:`assert_safe_write_target` refuses otherwise.

`FORBIDDEN_TARGETS` is the deny-list of every production dashboard + upstream
source id/URL taken from the Operations Runbook. If a future config ever points
the writer at one of these, we abort loudly before any network call.
"""

from __future__ import annotations

from typing import Iterable, Optional

# ---- Production dashboard (NEVER written by this skill) ----------------------
DASHBOARD_HEX_PROJECTS = {
    "CATS-Scorecard-030A2d4xbWcyM2JNhvw0Ks",     # published app / draft slug
    "019e470d-c9ad-7000-867d-c06152e12567",       # hex project id (push_cell.py)
    "Ads-Experimentation-Insights-031Wg80FsfMFpb7daAPehQ",
}

# ---- Upstream source spreadsheets / docs (READ-ONLY; never written) ----------
# Keyed for readability; only the ids matter for enforcement.
FORBIDDEN_SOURCE_IDS = {
    "1SDYpd5icuyBI-raKcaRX7zUBHjtxfWqz1aSj2x15Tvc",  # Governance sheet
    "1zQFWUxWWY0hIrnU1AVPGkEdJ9O1-emddDZMh0nxN-s8",  # Shopping pacing sheet
    "1obYe6RSkOoQG9gDKFJJNRO7FzvLm6LyTX7xXVwiXLdc",  # MAB Goaling 2026
    "1eu21vkHhHYNAFmY_tsxlCe3Gk1Mz_ieYdtZDT41gvXQ",  # DAUq Master
    "1_W3RgdwjMw9MMX9Bq3X99D0VFBFEamgSlUuJuvaxIH0",  # Daily Forecast - Live
    "1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw",  # CATS Roadmap Planning
    "1YidL22qkkaKdfbHX6EViyUCnTF2_dnl1vEDdE46obV0",  # Shopping 3H Tracker
    "1QbL630aVJMygNhIHg_dCSWeUNpzd_PDbWZjyQn9WWTk",  # Rev / S+M FTE
    "1rcmx-lOT73K5q19stLt7Io-UijoP9nkMrcrnyNFVu0s",  # Ads Launch Review Sign-up
    "1hox9yMMDwBwnJOGt9GiweFafCH7wWGGwsKlUfGWJ_sU",  # Manager Dashboard (OE)
    "1FHwfDergUSuQUV68f6j445i2_TQhBvpHeRlmie9SNEY",  # Efficiencies tracker (Cloud)
    "1s-Q0o19dG2b5sn25kHSXlWyqJ48vt9U39Vmi6DZU6r4",  # Ranking/Retrieval (Model V.)
    "10Q-ua5sQ4cUy3U1kvPO8kCS9I2m386mtwksWaMNDy_c",  # 2026 S-Scale Pillar doc
    "1tuD0BGUVPiMUd8jA8fckjteCLoqgBE6DnkgnzY2x2WA",  # S-pillar updates sheet (SOTA)
    "1wujsIOOkqapGknYdUNIjxekxpd90qsRM4ByoADJtvR8",  # Brand goals doc
}

FORBIDDEN_TARGETS = set(DASHBOARD_HEX_PROJECTS) | set(FORBIDDEN_SOURCE_IDS)

# Read-only OAuth scopes. The skill must never request a writable scope.
READONLY_SCOPES = (
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
)
_WRITE_SCOPE_MARKERS = ("spreadsheets", "drive", "documents")


class UnsafeWriteError(RuntimeError):
    """Raised when a write is attempted against a dashboard/source target."""


class UnsafeScopeError(RuntimeError):
    """Raised when a non-readonly OAuth scope is requested for a source read."""


def register_forbidden_ids(ids: Iterable[str]) -> None:
    """Add config-declared source ids to the deny-list (defensive superset)."""
    for i in ids:
        if i:
            FORBIDDEN_TARGETS.add(str(i))
            FORBIDDEN_SOURCE_IDS.add(str(i))


def assert_readonly_scopes(scopes: Iterable[str]) -> None:
    """Fail closed if any requested scope is not explicitly read-only."""
    for s in scopes:
        s = str(s)
        if any(m in s for m in _WRITE_SCOPE_MARKERS) and not s.endswith(".readonly"):
            raise UnsafeScopeError(
                "Refusing non-readonly source scope: %r. Sources are read-only." % s
            )


def assert_safe_write_target(target_id: Optional[str], kind: str) -> None:
    """Guarantee we only ever write to an isolated staging target.

    Aborts before any network/file call if ``target_id`` matches a known
    dashboard or source id. ``kind`` is 'google_sheet' or 'local_xlsx'.
    """
    if kind == "local_xlsx":
        return  # local isolated file — inherently not a dashboard/source
    if not target_id:
        raise UnsafeWriteError(
            "google_sheet staging target requires an explicit staging "
            "spreadsheet id (staging_target.google_spreadsheet_id)."
        )
    tid = str(target_id).strip()
    if tid in FORBIDDEN_TARGETS:
        raise UnsafeWriteError(
            "REFUSED: staging target %r is a known dashboard/source id. "
            "The skill writes only to an isolated staging sheet." % tid
        )


def is_forbidden(any_id: Optional[str]) -> bool:
    return bool(any_id) and str(any_id).strip() in FORBIDDEN_TARGETS
