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
