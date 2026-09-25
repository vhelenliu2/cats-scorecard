"""Safety guarantees: no dashboard/source writes, read-only scopes only."""

from __future__ import annotations

import pytest  # type: ignore

from cats_ingest import safety


def test_dashboard_and_sources_are_forbidden_targets():
    # Hex dashboard project + every source id must be write-forbidden.
    assert "019e470d-c9ad-7000-867d-c06152e12567" in safety.FORBIDDEN_TARGETS
    assert "1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw" in safety.FORBIDDEN_TARGETS  # Roadmap
    assert "1QbL630aVJMygNhIHg_dCSWeUNpzd_PDbWZjyQn9WWTk" in safety.FORBIDDEN_TARGETS  # Rev/FTE


def test_write_to_dashboard_is_refused():
    with pytest.raises(safety.UnsafeWriteError):
        safety.assert_safe_write_target(
            "1Dj-qIRj4tOXP_kdSBtOT2BFVTqzR4rws2VrwwkkuBmw", "google_sheet")


def test_google_write_requires_explicit_target():
    with pytest.raises(safety.UnsafeWriteError):
        safety.assert_safe_write_target(None, "google_sheet")


def test_local_xlsx_is_always_safe():
    # Local isolated file is inherently not a dashboard/source.
    safety.assert_safe_write_target(None, "local_xlsx")  # no raise


def test_isolated_staging_id_is_allowed():
    safety.assert_safe_write_target("SOME_NEW_STAGING_SHEET_ID_I_OWN", "google_sheet")


def test_non_readonly_scope_is_rejected():
    with pytest.raises(safety.UnsafeScopeError):
        safety.assert_readonly_scopes(
            ["https://www.googleapis.com/auth/spreadsheets"])  # writable


def test_readonly_scopes_pass():
    safety.assert_readonly_scopes(safety.READONLY_SCOPES)  # no raise
