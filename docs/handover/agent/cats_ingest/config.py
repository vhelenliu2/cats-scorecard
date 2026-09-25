"""Config loader for metric_config.yaml + goal/approval helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from . import safety
from .schema import CONFIRM

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "metric_config.yaml"


class Config:
    def __init__(self, data: Dict[str, Any], path: Path):
        self._d = data
        self.path = path

    # -- accessors ------------------------------------------------------------
    @property
    def sources(self) -> Dict[str, Any]:
        return self._d.get("sources", {})

    @property
    def metrics(self) -> Dict[str, Any]:
        return self._d.get("metrics", {})

    @property
    def goals(self) -> Dict[str, Any]:
        return self._d.get("goals", {})

    @property
    def staging_target(self) -> Dict[str, Any]:
        return self._d.get("staging_target", {})

    @property
    def tolerances(self) -> Dict[str, Any]:
        return self._d.get("tolerances", {})

    @property
    def credentials(self) -> Dict[str, Any]:
        return self._d.get("credentials", {})

    def source(self, source_id: str) -> Dict[str, Any]:
        return self.sources[source_id]

    def goal(self, goal_ref: str) -> Dict[str, Any]:
        return self.goals.get(goal_ref, {})

    def source_url(self, source_id: str) -> str:
        s = self.sources.get(source_id, {})
        sid = s.get("spreadsheet_id")
        if sid:
            gid = s.get("gid")
            base = "https://docs.google.com/spreadsheets/d/%s" % sid
            return base + ("/edit#gid=%s" % gid if gid is not None else "")
        if s.get("document_id"):
            return "https://docs.google.com/document/d/%s" % s["document_id"]
        if s.get("hex_app"):
            return "https://app.hex.tech/reddit/app/%s/latest" % s["hex_app"]
        return s.get("query_ref", "")


def load_config(path: Optional[Path] = None) -> Config:
    p = Path(path) if path else DEFAULT_CONFIG_PATH
    with p.open() as f:
        data = yaml.safe_load(f)
    cfg = Config(data, p)
    # Defensive: register every declared source id into the write deny-list.
    ids: List[str] = []
    for s in cfg.sources.values():
        for key in ("spreadsheet_id", "document_id"):
            if s.get(key):
                ids.append(str(s[key]))
    safety.register_forbidden_ids(ids)
    return cfg


# ---- approval / confirmation helpers ----------------------------------------

def is_confirmed(value: Any) -> bool:
    """A value is 'confirmed' only if it is present and not the CONFIRM sentinel."""
    if value is None:
        return False
    if isinstance(value, str) and value.strip() == CONFIRM:
        return False
    return True


def goal_is_approved(goal: Dict[str, Any]) -> bool:
    return goal.get("approval_status") == "approved"
