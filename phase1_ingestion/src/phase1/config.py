from __future__ import annotations

import os
from dataclasses import dataclass


def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class IngestionFlags:
    enable_reddit_ingestion: bool
    enable_trustpilot_ingestion: bool
    enable_g2_ingestion: bool
    enable_google_play_ingestion: bool
    enable_one_time_playwright_backfill: bool
    safe_mode: bool
    allow_non_safe_sources: bool


def load_flags() -> IngestionFlags:
    return IngestionFlags(
        enable_reddit_ingestion=_bool_env("ENABLE_REDDIT_INGESTION", True),
        enable_trustpilot_ingestion=_bool_env("ENABLE_TRUSTPILOT_INGESTION", False),
        enable_g2_ingestion=_bool_env("ENABLE_G2_INGESTION", False),
        enable_google_play_ingestion=_bool_env("ENABLE_GOOGLE_PLAY_INGESTION", False),
        enable_one_time_playwright_backfill=_bool_env("ENABLE_ONE_TIME_PLAYWRIGHT_BACKFILL", False),
        safe_mode=_bool_env("SAFE_MODE", True),
        allow_non_safe_sources=_bool_env("ALLOW_NON_SAFE_SOURCES", False),
    )

