import json
import re
import unicodedata
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any


EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"\b(?:\+?\d[\d\s().-]{7,}\d)\b")
USERNAME_RE = re.compile(r"@\w+")
LINK_RE = re.compile(r"https?://\S+")
HTML_RE = re.compile(r"<[^>]*>")
SPACE_RE = re.compile(r"\s+")


@dataclass
class CleanReview:
    source: str
    text: str
    created_at_utc: str
    language: str
    dedupe_key: str
    author_id_hash: str | None = None
    rating: float | None = None
    title: str | None = None
    source_review_id: str | None = None
    source_url: str | None = None
    is_one_word: bool = False
    subreddit: str | None = None


def redact_pii(text: str) -> str:
    text = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = PHONE_RE.sub("[REDACTED_PHONE]", text)
    text = USERNAME_RE.sub("[REDACTED_USER]", text)
    text = LINK_RE.sub("[REDACTED_LINK]", text)
    return text


def normalize_text(text: str) -> str:
    # Strip HTML
    text = HTML_RE.sub(" ", text)
    # Unicode normalization
    text = unicodedata.normalize("NFKC", text)
    # Collapse whitespace
    return SPACE_RE.sub(" ", text).strip()


def is_one_word(text: str) -> bool:
    # Use a simpler check for token count
    tokens = [w for w in text.split(" ") if w.strip()]
    return len(tokens) <= 1


def within_last_n_days(created_at_utc: str, *, now_utc: datetime, days: int) -> bool:
    try:
        created = datetime.fromisoformat(created_at_utc)
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        return created >= (now_utc - timedelta(days=days))
    except (ValueError, TypeError):
        return False


def _language_ok(language: str) -> bool:
    return language.lower().startswith("en")


def _get_fuzzy_key(source: str, text: str) -> str:
    # Normalize for fuzzy dedupe: lowercase, remove non-alphanumeric, collapse space
    norm = re.sub(r"[^a-z0-9]", "", text.lower())
    return sha256(f"{source}|{norm}".encode("utf-8")).hexdigest()


def preprocess_reviews(records: list[dict[str, Any]], *, now_utc: datetime | None = None) -> list[CleanReview]:
    now = now_utc or datetime.now(timezone.utc)
    seen: set[str] = set()
    output: list[CleanReview] = []

    for record in records:
        source = str(record.get("source", "")).strip() or "unknown"
        text_raw = str(record.get("text", "")).strip()
        created_at_utc = str(record.get("date", "")).strip()
        language = str(record.get("language", "en")).strip() or "en"
        
        # Additional fields
        rating = record.get("rating") or record.get("score")
        title = record.get("title")
        source_review_id = record.get("source_review_id")
        source_url = record.get("source_url")
        author_raw = record.get("author") or record.get("username")
        subreddit = record.get("subreddit")

        if not text_raw:
            continue
        if not _language_ok(language):
            continue

        if not created_at_utc:
            created_at_utc = now.isoformat()

        # Handle YYYY-MM-DD
        if len(created_at_utc) == 10:
            created_at_utc = f"{created_at_utc}T00:00:00+00:00"

        if not within_last_n_days(created_at_utc, now_utc=now, days=30):
            continue

        # Normalize and redact
        text = normalize_text(redact_pii(text_raw))
        
        # Check one-word
        one_word = is_one_word(text)
        if not text:
            continue

        # Deduplication (Fuzzy)
        dedupe_key = _get_fuzzy_key(source, text)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        # Author ID anonymization
        author_id_hash = None
        if author_raw:
            author_id_hash = sha256(str(author_raw).encode("utf-8")).hexdigest()

        output.append(
            CleanReview(
                source=source,
                text=text,
                created_at_utc=created_at_utc,
                language=language,
                dedupe_key=dedupe_key,
                author_id_hash=author_id_hash,
                rating=float(rating) if rating is not None else None,
                title=title,
                source_review_id=source_review_id,
                source_url=source_url,
                is_one_word=one_word,
                subreddit=subreddit
            )
        )
    return output


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save_clean_json(path: Path, reviews: list[CleanReview]) -> None:
    payload = [asdict(r) for r in reviews]
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def run_phase2(input_path: Path, output_path: Path, *, now_utc: datetime | None = None) -> int:
    raw = load_json(input_path)
    if not isinstance(raw, list):
        # Handle the case where the input is a dictionary with a "reviews" key
        if isinstance(raw, dict) and "reviews" in raw:
            raw = raw["reviews"]
        else:
            raise ValueError("Input JSON must be an array of review objects or a dict with a 'reviews' key.")
    cleaned = preprocess_reviews(raw, now_utc=now_utc)
    save_clean_json(output_path, cleaned)
    return len(cleaned)

