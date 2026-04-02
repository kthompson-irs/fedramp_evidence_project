from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EvidenceStatus(str, Enum):
    ready = "Ready"
    pending = "Pending"
    failed = "Failed"


class EvidenceItem(BaseModel):
    control_id: str
    control_family: str
    source: str
    artifact_type: str
    artifact_name: str
    timestamp_utc: str
    status: EvidenceStatus = EvidenceStatus.ready
    owner: Optional[str] = None
    evidence_uri: Optional[str] = None
    checksum: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class CollectorHealth(BaseModel):
    source: str
    healthy: bool
    last_run_utc: str
    message: Optional[str] = None


class Snapshot(BaseModel):
    generated_at_utc: str
    evidence_count: int
    ready_count: int
    pending_count: int
    failed_count: int
    collectors: List[CollectorHealth]
    evidence: List[EvidenceItem]
[wnglb@vp2smtbappiem02 app]$ ls
collectors  config.py  exporters  __init__.py  main.py  models.py  services  store.py  utils.py
[wnglb@vp2smtbappiem02 app]$ cat store.py
from __future__ import annotations

from typing import List

from .models import CollectorHealth, EvidenceItem, Snapshot
from .utils import utc_now


class DashboardStore:
    def __init__(self) -> None:
        self._items: List[EvidenceItem] = []
        self._collectors: List[CollectorHealth] = []
        self._updated_at = utc_now()

    def refresh(self, items: List[EvidenceItem], collectors: List[CollectorHealth]) -> None:
        self._items = items
        self._collectors = collectors
        self._updated_at = utc_now()

    def snapshot(self) -> Snapshot:
        ready = sum(1 for item in self._items if item.status == "Ready")
        pending = sum(1 for item in self._items if item.status == "Pending")
        failed = sum(1 for item in self._items if item.status == "Failed")
        return Snapshot(
            generated_at_utc=self._updated_at,
            evidence_count=len(self._items),
            ready_count=ready,
            pending_count=pending,
            failed_count=failed,
            collectors=self._collectors,
            evidence=self._items,
        )
[wnglb@vp2smtbappiem02 app]$ ls
collectors  config.py  exporters  __init__.py  main.py  models.py  services  store.py  utils.py
[wnglb@vp2smtbappiem02 app]$ cat utils.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_len(value: Any) -> int:
    try:
        return len(value)
    except Exception:
        return 0
