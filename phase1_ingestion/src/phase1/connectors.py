from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass
from typing import Iterable

from phase1.capabilities import ComplianceLevel
from phase1.models import RawItem


class SourceConnector(ABC):
    source_name: str
    access_type: str
    compliance_level: ComplianceLevel
    enabled_by_default: bool
    requires_api_key: bool
    max_requests_per_minute: int
    max_requests_per_day: int
    max_items_per_run: int

    @abstractmethod
    def fetch_since(self, since_datetime_utc: datetime) -> Iterable[RawItem]:
        """Return raw items since the provided timestamp."""


@dataclass
class AdapterUsage:
    api_calls_used: int = 0
    estimated_cost: float = 0.0
    records_fetched: int = 0


class BaseAdapter(SourceConnector):
    def __init__(
        self,
        source_name: str,
        access_type: str,
        compliance_level: ComplianceLevel,
        enabled_by_default: bool,
        requires_api_key: bool,
        max_requests_per_minute: int,
        max_requests_per_day: int,
        max_items_per_run: int,
    ):
        self.source_name = source_name
        self.access_type = access_type
        self.compliance_level = compliance_level
        self.enabled_by_default = enabled_by_default
        self.requires_api_key = requires_api_key
        self.max_requests_per_minute = max_requests_per_minute
        self.max_requests_per_day = max_requests_per_day
        self.max_items_per_run = max_items_per_run
        self.last_usage = AdapterUsage()


class ApiAdapter(BaseAdapter):
    def __init__(
        self,
        source_name: str,
        *,
        compliance_level: ComplianceLevel = "safe",
        enabled_by_default: bool = True,
        requires_api_key: bool = True,
        max_requests_per_minute: int = 60,
        max_requests_per_day: int = 5000,
        max_items_per_run: int = 1000,
    ):
        super().__init__(
            source_name=source_name,
            access_type="API",
            compliance_level=compliance_level,
            enabled_by_default=enabled_by_default,
            requires_api_key=requires_api_key,
            max_requests_per_minute=max_requests_per_minute,
            max_requests_per_day=max_requests_per_day,
            max_items_per_run=max_items_per_run,
        )


class ScrapingAdapter(BaseAdapter):
    def __init__(
        self,
        source_name: str,
        *,
        compliance_level: ComplianceLevel = "high-risk",
        enabled_by_default: bool = False,
        max_requests_per_minute: int = 10,
        max_requests_per_day: int = 500,
        max_items_per_run: int = 200,
    ):
        super().__init__(
            source_name=source_name,
            access_type="scraping",
            compliance_level=compliance_level,
            enabled_by_default=enabled_by_default,
            requires_api_key=False,
            max_requests_per_minute=max_requests_per_minute,
            max_requests_per_day=max_requests_per_day,
            max_items_per_run=max_items_per_run,
        )

    def fetch_since(self, since_datetime_utc: datetime) -> Iterable[RawItem]:
        # Scraping logic is intentionally not implemented in this codebase.
        self.last_usage = AdapterUsage(api_calls_used=0, estimated_cost=0.0, records_fetched=0)
        return []


class StubAdapter(BaseAdapter):
    def __init__(
        self,
        source_name: str,
        *,
        access_type: str,
        compliance_level: ComplianceLevel,
        requires_api_key: bool,
    ):
        super().__init__(
            source_name=source_name,
            access_type=access_type,
            compliance_level=compliance_level,
            enabled_by_default=False,
            requires_api_key=requires_api_key,
            max_requests_per_minute=0,
            max_requests_per_day=0,
            max_items_per_run=0,
        )

    def fetch_since(self, since_datetime_utc: datetime) -> Iterable[RawItem]:
        return []


class StaticApiAdapter(ApiAdapter):
    """
    Test-friendly connector that returns preloaded items.
    In production, replace with concrete API adapters.
    """

    def __init__(self, source_name: str, items: list[RawItem], max_items_per_run: int = 1000):
        super().__init__(source_name=source_name, max_items_per_run=max_items_per_run)
        self._items = items

    def fetch_since(self, since_datetime_utc: datetime) -> Iterable[RawItem]:
        result: list[RawItem] = []
        for item in self._items:
            created_raw = item.payload.get("created_at_utc")
            if not created_raw:
                continue
            created = datetime.fromisoformat(created_raw)
            if created >= since_datetime_utc:
                result.append(item)
            if len(result) >= self.max_items_per_run:
                break
        self.last_usage = AdapterUsage(
            api_calls_used=1,
            estimated_cost=0.0,
            records_fetched=len(result),
        )
        return result
