import pytest
from datetime import datetime, timezone, timedelta
from phase4.analytics import AnalyticsEngine

def test_trend_calculation():
    now = datetime(2026, 4, 30, tzinfo=timezone.utc)
    engine = AnalyticsEngine(now_utc=now)
    
    # Mock reviews
    reviews = [
        # Current 7 days
        {"themes": ["Issue A"], "created_at_utc": (now - timedelta(days=2)).isoformat(), "sentiment_score": -0.5},
        {"themes": ["Issue A"], "created_at_utc": (now - timedelta(days=3)).isoformat(), "sentiment_score": -0.6},
        # Previous 7 days (days 8-14)
        {"themes": ["Issue A"], "created_at_utc": (now - timedelta(days=9)).isoformat(), "sentiment_score": -0.4},
    ]
    
    top_issues = [
        {
            "issue_id": "issue_a",
            "theme": "Issue A",
            "descriptive_title": "Test Issue",
            "detailed_description": "Desc",
            "metrics": {"avg_sentiment": -0.5},
            "evidence_snippets": ["Snippet 1"]
        }
    ]
    
    results = engine.calculate_trends(reviews, top_issues)
    
    assert len(results) == 1
    metrics = results[0]["metrics"]
    assert metrics["current_7d_count"] == 2
    assert metrics["previous_7d_count"] == 1
    assert metrics["trend_percentage"] == 100.0
    assert metrics["total_mentions_30d"] == 3
    assert metrics["sentiment_distribution"]["negative"] == 3

def test_no_data_trend():
    now = datetime(2026, 4, 30, tzinfo=timezone.utc)
    engine = AnalyticsEngine(now_utc=now)
    
    results = engine.calculate_trends([], [{
        "issue_id": "x", 
        "theme": "Y", 
        "descriptive_title": "T", 
        "detailed_description": "D", 
        "metrics": {"avg_sentiment": 0},
        "evidence_snippets": []
    }])
    assert results[0]["metrics"]["trend_percentage"] == 0.0
