from __future__ import annotations

import hashlib
import re
from datetime import datetime, timedelta, timezone
from typing import Iterable

from phase1.capabilities import SOURCE_CAPABILITY_MATRIX
from phase1.config import IngestionFlags, load_flags
from phase1.connectors import ApiAdapter, SourceConnector
from phase1.models import NormalizedReview, RawItem
from phase1.storage import JsonlStorage


PII_PATTERNS = [
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\b(?:\+?\d[\d\s().-]{7,}\d)\b"),
]


def redact_pii(text: str) -> str:
    redacted = text
    for pattern in PII_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def normalize_raw_item(item: RawItem, ingested_at_utc: datetime) -> NormalizedReview:
    payload = item.payload
    text = redact_pii(payload.get("body_text", "").strip())
    words = [w for w in text.split() if w.strip()]
    author_raw = payload.get("author", "unknown")
    author_hash = hashlib.sha256(author_raw.encode("utf-8")).hexdigest()
    dedupe_key = hashlib.sha256(f"{item.source}|{text}".encode("utf-8")).hexdigest()

    return NormalizedReview(
        source=item.source,
        source_review_id=item.source_review_id,
        source_url=item.source_url,
        author_id_hash=author_hash,
        body_text=text,
        created_at_utc=datetime.fromisoformat(payload["created_at_utc"]),
        ingested_at_utc=ingested_at_utc,
        language=payload.get("language", "en"),
        is_one_word=len(words) == 1,
        dedupe_key=dedupe_key,
        rating=payload.get("rating"),
        title=payload.get("title"),
    )


def _is_enabled(source_name: str, flags: IngestionFlags) -> bool:
    if source_name.startswith("reddit_"):
        return flags.enable_reddit_ingestion
    if source_name == "trustpilot_claude_ai":
        return flags.enable_trustpilot_ingestion
    if source_name == "g2_claude_reviews":
        return flags.enable_g2_ingestion
    if source_name == "google_play_claude":
        return flags.enable_google_play_ingestion
    return False


def run_phase1_ingestion(
    connectors: Iterable[SourceConnector],
    storage: JsonlStorage,
    now_utc: datetime | None = None,
    flags: IngestionFlags | None = None,
) -> dict[str, object]:
    now = now_utc or datetime.now(timezone.utc)
    since = now - timedelta(days=30)
    run_flags = flags or load_flags()
    counts: dict[str, int] = {}
    usage: dict[str, dict[str, float | int]] = {}
    skipped: dict[str, str] = {}
    total_api_calls = 0
    total_estimated_cost = 0.0
    total_records = 0

    for connector in connectors:
        capability = SOURCE_CAPABILITY_MATRIX.get(connector.source_name)
        if capability is None:
            skipped[connector.source_name] = "missing_capability_matrix"
            continue

        if not _is_enabled(connector.source_name, run_flags):
            skipped[connector.source_name] = "feature_flag_disabled"
            continue

        if connector.access_type == "scraping" and not run_flags.enable_one_time_playwright_backfill:
            skipped[connector.source_name] = "one_time_playwright_disabled"
            continue

        if run_flags.safe_mode and connector.access_type != "API":
            skipped[connector.source_name] = "blocked_by_safe_mode"
            continue

        if capability.compliance_level != "safe" and not run_flags.allow_non_safe_sources:
            skipped[connector.source_name] = "blocked_by_compliance_gate"
            continue

        if not isinstance(connector, ApiAdapter):
            skipped[connector.source_name] = "phase1_api_only"
            continue

        raw_items = list(connector.fetch_since(since))
        if len(raw_items) > connector.max_items_per_run:
            raw_items = raw_items[: connector.max_items_per_run]
        storage.write_raw(connector.source_name, raw_items)
        normalized = [normalize_raw_item(item, ingested_at_utc=now) for item in raw_items]
        storage.write_normalized(connector.source_name, normalized)
        counts[connector.source_name] = len(raw_items)
        usage[connector.source_name] = {
            "api_calls_used": connector.last_usage.api_calls_used,
            "estimated_cost": connector.last_usage.estimated_cost,
            "records_fetched": connector.last_usage.records_fetched,
        }
        total_api_calls += connector.last_usage.api_calls_used
        total_estimated_cost += connector.last_usage.estimated_cost
        total_records += connector.last_usage.records_fetched

    run_log = {
        "run_at_utc": now.isoformat(),
        "safe_mode": run_flags.safe_mode,
        "counts": counts,
        "usage": usage,
        "skipped": skipped,
        "totals": {
            "api_calls_used": total_api_calls,
            "estimated_cost": round(total_estimated_cost, 6),
            "records_fetched": total_records,
        },
    }
    storage.write_run_log(run_log)
    return run_log

