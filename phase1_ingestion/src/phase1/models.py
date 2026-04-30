from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class RawItem:
    source: str
    source_review_id: str
    source_url: str
    payload: dict[str, Any]
    fetched_at_utc: datetime


@dataclass
class NormalizedReview:
    source: str
    source_review_id: str
    source_url: str
    author_id_hash: str
    body_text: str
    created_at_utc: datetime
    ingested_at_utc: datetime
    language: str
    is_one_word: bool
    dedupe_key: str
    rating: float | None = None
    title: str | None = None

