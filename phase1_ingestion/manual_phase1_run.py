from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from phase1.config import IngestionFlags
from phase1.connectors import StaticApiAdapter, StubAdapter
from phase1.models import RawItem
from phase1.pipeline import run_phase1_ingestion
from phase1.storage import JsonlStorage


def _raw(source: str, rid: str, body: str, created: datetime) -> RawItem:
    return RawItem(
        source=source,
        source_review_id=rid,
        source_url=f"https://example.com/{source}/{rid}",
        payload={
            "author": "manual_user",
            "body_text": body,
            "created_at_utc": created.isoformat(),
            "language": "en",
            "rating": 4.0,
        },
        fetched_at_utc=datetime.now(timezone.utc),
    )


def main() -> None:
    now = datetime.now(timezone.utc)
    within_30_days = now - timedelta(days=5)
    older_than_30_days = now - timedelta(days=45)

    connectors = [
        StaticApiAdapter("reddit_claudeai", [_raw("reddit_claudeai", "1", "token limits are annoying", within_30_days)]),
        StaticApiAdapter("reddit_claude", [_raw("reddit_claude", "1", "model got slower recently", within_30_days)]),
        StaticApiAdapter("reddit_claudeskills", [_raw("reddit_claudeskills", "1", "contact me at test@example.com", within_30_days)]),
        StaticApiAdapter("reddit_claude", [_raw("reddit_claude", "2", "old data", older_than_30_days)]),
        StubAdapter("trustpilot_claude_ai", access_type="scraping", compliance_level="high-risk", requires_api_key=False),
    ]

    flags = IngestionFlags(
        enable_reddit_ingestion=True,
        enable_trustpilot_ingestion=False,
        enable_g2_ingestion=False,
        enable_google_play_ingestion=False,
        enable_one_time_playwright_backfill=False,
        safe_mode=True,
        allow_non_safe_sources=False,
    )

    output_dir = Path("manual_artifacts")
    storage = JsonlStorage(output_dir)
    run_log = run_phase1_ingestion(connectors, storage, now_utc=now, flags=flags)
    print(run_log)


if __name__ == "__main__":
    main()

