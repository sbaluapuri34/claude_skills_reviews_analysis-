from __future__ import annotations

from datetime import datetime, timezone

from phase2.preprocess import preprocess_reviews


def test_phase2_filters_and_normalizes() -> None:
    now = datetime(2026, 4, 30, tzinfo=timezone.utc)
    records = [
        {"source": "google_play", "text": "Great app", "date": "2026-04-29", "language": "en"},
        {"source": "google_play", "text": "Great app!", "date": "2026-04-29", "language": "en"},  # fuzzy duplicate
        {"source": "google_play", "text": "Nice", "date": "2026-04-29", "language": "en"},  # one-word
        {"source": "google_play", "text": "Mon email is user@example.com", "date": "2026-04-28", "language": "en"},
        {"source": "google_play", "text": "Hola mundo", "date": "2026-04-28", "language": "es"},  # non-english
        {"source": "google_play", "text": "old review", "date": "2026-02-01", "language": "en"},  # older than 30 days
        {"source": "google_play", "text": "Check out <html>tags</html>", "date": "2026-04-29", "language": "en"},
    ]

    out = preprocess_reviews(records, now_utc=now)
    # 1. Great app
    # 2. Nice (one-word)
    # 3. Mon email is [REDACTED_EMAIL]
    # 4. Check out tags
    assert len(out) == 4
    texts = [item.text for item in out]
    assert "Great app" in texts
    assert any("[REDACTED_EMAIL]" in text for text in texts)
    assert "Check out tags" in texts
    
    nice_review = next(r for r in out if r.text == "Nice")
    assert nice_review.is_one_word is True

