from __future__ import annotations
import json
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class IssueTrend:
    issue_id: str
    title: str
    current_7d_mentions: int
    previous_7d_mentions: int
    trend_percentage: float
    total_30d_mentions: int
    sentiment_split: Dict[str, int]
    evidence_snippets: List[str]

class AnalyticsEngine:
    def __init__(self, now_utc: datetime | None = None):
        self.now = now_utc or datetime.now(timezone.utc)

    def calculate_trends(self, reviews: List[Dict], top_issues: List[Dict]) -> List[Dict]:
        results = []
        
        # Helper to categorize date
        def get_days_ago(dt_str):
            try:
                dt = datetime.fromisoformat(dt_str)
                if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
                return (self.now - dt).days
            except:
                return 999

        for issue in top_issues:
            issue_id = issue["issue_id"]
            theme = issue["theme"]
            
            # Filter reviews belonging to this theme
            issue_reviews = [r for r in reviews if theme in r.get("themes", [])]
            
            # Sentiment split
            sentiment_split = {"positive": 0, "neutral": 0, "negative": 0}
            for r in issue_reviews:
                score = r.get("sentiment_score", 0.0)
                if score > 0.2: sentiment_split["positive"] += 1
                elif score < -0.2: sentiment_split["negative"] += 1
                else: sentiment_split["neutral"] += 1
            
            # Trends
            current_7d = 0
            previous_7d = 0
            total_30d = 0
            
            for r in issue_reviews:
                days_ago = get_days_ago(r.get("created_at_utc"))
                if days_ago <= 7:
                    current_7d += 1
                    total_30d += 1
                elif days_ago <= 14:
                    previous_7d += 1
                    total_30d += 1
                elif days_ago <= 30:
                    total_30d += 1
            
            # Trend percentage
            if previous_7d == 0:
                trend_pct = 100.0 if current_7d > 0 else 0.0
            else:
                trend_pct = ((current_7d - previous_7d) / previous_7d) * 100.0
                
            results.append({
                "issue_id": issue_id,
                "theme": theme,
                "title": issue["descriptive_title"],
                "description": issue["detailed_description"],
                "metrics": {
                    "total_mentions_30d": total_30d,
                    "current_7d_count": current_7d,
                    "previous_7d_count": previous_7d,
                    "trend_percentage": round(trend_pct, 1),
                    "avg_sentiment": issue["metrics"]["avg_sentiment"],
                    "sentiment_distribution": sentiment_split
                },
                "evidence": issue["evidence_snippets"]
            })
            
        return results

def run_analytics(reviews_path: str, issues_path: str, output_path: str, now_utc: datetime | None = None):
    with open(reviews_path, "r", encoding="utf-8") as f:
        reviews = json.load(f)
    with open(issues_path, "r", encoding="utf-8") as f:
        top_issues_map = json.load(f)
        
    engine = AnalyticsEngine(now_utc=now_utc)
    final_analytics = {}
    
    for source, issues in top_issues_map.items():
        # Filter reviews for this source
        source_reviews = [r for r in reviews if (r.get("subreddit") == source or r.get("source") == source)]
        final_analytics[source] = engine.calculate_trends(source_reviews, issues)
        
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_analytics, f, indent=2, ensure_ascii=False)
        
    return final_analytics
