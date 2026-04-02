from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ..models import CollectorHealth, EvidenceItem
from ..utils import utc_now


class BaseCollector(ABC):
    @abstractmethod
    def collect(self) -> List[EvidenceItem]:
        raise NotImplementedError

    def health(self, healthy: bool, message: str | None = None) -> CollectorHealth:
        return CollectorHealth(
            source=self.__class__.__name__,
            healthy=healthy,
            last_run_utc=utc_now(),
            message=message,
        )   
