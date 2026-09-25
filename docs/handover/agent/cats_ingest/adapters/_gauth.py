"""Google read-only auth helper. Credentials referenced BY NAME only.

The credential is resolved from an environment variable whose NAME is given in
config (`credentials.google_sheets`). The value may be either:
  * a filesystem path to a service-account JSON, or
  * the service-account JSON content itself.

We only ever request READ-ONLY scopes (enforced by safety.assert_readonly_scopes).
Nothing is logged. Missing credentials return None so callers degrade to a
MISSING envelope instead of crashing.
"""

from __future__ import annotations

import json
import os
from typing import Optional

from .. import safety


def _load_sa_info(raw: str):
    raw = raw.strip()
    if raw.startswith("{"):
        return json.loads(raw)
    if os.path.exists(raw):
        with open(raw) as f:
            return json.load(f)
    return None


def get_readonly_client(cred_env_name: str):
    """Return an authorized gspread client (read-only) or None if unavailable.

    Never raises for missing creds; raises only if an unsafe scope slips in.
    """
    safety.assert_readonly_scopes(safety.READONLY_SCOPES)

    raw = os.environ.get(cred_env_name)
    if not raw:
        return None
    info = _load_sa_info(raw)
    if not info:
        return None
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        creds = Credentials.from_service_account_info(
            info, scopes=list(safety.READONLY_SCOPES)
        )
        return gspread.authorize(creds)
    except Exception:
        return None


def get_readonly_credentials(cred_env_name: str):
    """Return google Credentials (read-only) for Docs API, or None."""
    safety.assert_readonly_scopes(safety.READONLY_SCOPES)
    raw = os.environ.get(cred_env_name)
    if not raw:
        return None
    info = _load_sa_info(raw)
    if not info:
        return None
    try:
        from google.oauth2.service_account import Credentials

        return Credentials.from_service_account_info(
            info, scopes=list(safety.READONLY_SCOPES)
        )
    except Exception:
        return None
