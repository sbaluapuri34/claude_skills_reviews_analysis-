from __future__ import annotations

from datetime import datetime
from typing import Iterable

from phase1.connectors import ApiAdapter, ScrapingAdapter, StubAdapter
from phase1.models import RawItem


class RedditApiAdapter(ApiAdapter):
    """
    Official API adapter placeholder for Reddit.
    Keep this API-only in Phase 1; no scraping fallback allowed.
    """

    def __init__(self, source_name: str):
        super().__init__(
            source_name=source_name,
            compliance_level="safe",
            enabled_by_default=True,
            requires_api_key=True,
            max_requests_per_minute=60,
            max_requests_per_day=5000,
            max_items_per_run=1000,
        )

    def fetch_since(self, since_datetime_utc: datetime) -> Iterable[RawItem]:
        # TODO: Integrate official Reddit API client.
        self.last_usage.api_calls_used = 0
        self.last_usage.estimated_cost = 0.0
        self.last_usage.records_fetched = 0
        return []


class OneTimePlaywrightStubAdapter(ScrapingAdapter):
    """
    Manual one-time Playwright backfill placeholder.
    Disabled by default and blocked by SAFE_MODE unless explicitly overridden.
    """

    def __init__(self, source_name: str):
        super().__init__(
            source_name=source_name,
            compliance_level="high-risk",
            enabled_by_default=False,
            max_requests_per_minute=5,
            max_requests_per_day=100,
            max_items_per_run=500,
        )


def build_phase1_adapters() -> list[ApiAdapter | StubAdapter | ScrapingAdapter]:
    return [
        RedditApiAdapter("reddit_claudeai"),
        RedditApiAdapter("reddit_claude"),
        RedditApiAdapter("reddit_claudeskills"),
        StubAdapter(
            "trustpilot_claude_ai",
            access_type="scraping",
            compliance_level="high-risk",
            requires_api_key=False,
        ),
        StubAdapter(
            "g2_claude_reviews",
            access_type="scraping",
            compliance_level="high-risk",
            requires_api_key=False,
        ),
        StubAdapter(
            "google_play_claude",
            access_type="partner_api",
            compliance_level="restricted",
            requires_api_key=True,
        ),
    ]


def build_one_time_playwright_backfill_adapters() -> list[OneTimePlaywrightStubAdapter]:
    return [
        OneTimePlaywrightStubAdapter("trustpilot_claude_ai"),
        OneTimePlaywrightStubAdapter("g2_claude_reviews"),
        OneTimePlaywrightStubAdapter("google_play_claude"),
    ]

