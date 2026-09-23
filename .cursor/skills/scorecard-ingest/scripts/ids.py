"""Stable IDs — same rule as governance/build_seed.py and apply_governance_warnings.py."""

from __future__ import annotations

import hashlib


def stable_id(prefix: str, value: str) -> str:
    suffix = hashlib.sha256(value.strip().encode()).hexdigest()[:12].upper()
    return f"{prefix}-{suffix}"


def metric_id_for_display(display_name: str) -> str:
    return stable_id("MET", display_name)
