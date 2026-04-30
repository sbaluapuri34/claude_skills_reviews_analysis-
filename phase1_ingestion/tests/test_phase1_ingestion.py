import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from phase1.config import IngestionFlags
from phase1.connectors import StaticApiAdapter, StubAdapter
from phase1.models import RawItem
from phase1.pipeline import run_phase1_ingestion
from phase1.storage import JsonlStorage


def _raw(source: str, rid: str, body: str, created: datetime, author: str = "user_1") -> RawItem:
    return RawItem(
        source=source,
        source_review_id=rid,
        source_url=f"https://example.com/{source}/{rid}",
        payload={
            "author": author,
            "body_text": body,
            "created_at_utc": created.isoformat(),
            "language": "en",
            "rating": 4.0,
        },
        fetched_at_utc=datetime.now(timezone.utc),
    )


def test_phase1_ingestion_writes_raw_and_normalized_with_30_day_filter(tmp_path: Path) -> None:
    now = datetime(2026, 4, 30, tzinfo=timezone.utc)
    within_30_days = now - timedelta(days=10)

    connectors = [
        StaticApiAdapter("reddit_claudeai", [_raw("reddit_claudeai", "1", "limits", within_30_days)]),
        StaticApiAdapter("reddit_claude", [_raw("reddit_claude", "1", "model got slower recently", within_30_days)]),
        StaticApiAdapter("reddit_claudeskills", [_raw("reddit_claudeskills", "1", "my email is a@b.com", within_30_days)]),
        StubAdapter("trustpilot_claude_ai", access_type="scraping", compliance_level="high-risk", requires_api_key=False),
        StubAdapter("google_play_claude", access_type="partner_api", compliance_level="restricted", requires_api_key=True),
        StubAdapter("g2_claude_reviews", access_type="scraping", compliance_level="high-risk", requires_api_key=False),
    ]

    storage = JsonlStorage(base_dir=tmp_path / "artifacts")
    flags = IngestionFlags(
        enable_reddit_ingestion=True,
        enable_trustpilot_ingestion=False,
        enable_g2_ingestion=False,
        enable_google_play_ingestion=False,
        enable_one_time_playwright_backfill=False,
        safe_mode=True,
        allow_non_safe_sources=False,
    )
    run_log = run_phase1_ingestion(connectors, storage, now_utc=now, flags=flags)

    counts = run_log["counts"]
    skipped = run_log["skipped"]
    totals = run_log["totals"]

    assert counts["reddit_claudeai"] == 1
    assert counts["reddit_claude"] == 1
    assert counts["reddit_claudeskills"] == 1
    assert "trustpilot_claude_ai" in skipped
    assert "google_play_claude" in skipped
    assert "g2_claude_reviews" in skipped
    assert totals["records_fetched"] == 3
    assert totals["api_calls_used"] == 3

    normalized_reddit_claudeskills = (tmp_path / "artifacts" / "normalized" / "reddit_claudeskills.jsonl").read_text(encoding="utf-8")
    assert "[REDACTED]" in normalized_reddit_claudeskills
    assert "a@b.com" not in normalized_reddit_claudeskills

    normalized_reddit_claudeai = (tmp_path / "artifacts" / "normalized" / "reddit_claudeai.jsonl").read_text(encoding="utf-8")
    line = json.loads(normalized_reddit_claudeai.strip())
    assert line["is_one_word"] is True

    run_log_path = tmp_path / "artifacts" / "run_log.json"
    assert run_log_path.exists()


def test_phase1_blocks_one_time_playwright_in_safe_mode(tmp_path: Path) -> None:
    now = datetime(2026, 4, 30, tzinfo=timezone.utc)
    within_30_days = now - timedelta(days=10)
    connectors = [
        StaticApiAdapter("reddit_claudeai", [_raw("reddit_claudeai", "1", "good", within_30_days)]),
        StubAdapter("trustpilot_claude_ai", access_type="scraping", compliance_level="high-risk", requires_api_key=False),
    ]
    storage = JsonlStorage(base_dir=tmp_path / "artifacts")
    flags = IngestionFlags(
        enable_reddit_ingestion=True,
        enable_trustpilot_ingestion=True,
        enable_g2_ingestion=False,
        enable_google_play_ingestion=False,
        enable_one_time_playwright_backfill=True,
        safe_mode=True,
        allow_non_safe_sources=True,
    )

    run_log = run_phase1_ingestion(connectors, storage, now_utc=now, flags=flags)
    assert run_log["counts"]["reddit_claudeai"] == 1
    assert run_log["skipped"]["trustpilot_claude_ai"] == "blocked_by_safe_mode"

