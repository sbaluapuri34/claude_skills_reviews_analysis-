import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from phase4.analytics import run_analytics

def main():
    parser = argparse.ArgumentParser(description="Run Phase 4: Detailed Analytics and Trends.")
    parser.add_argument("--reviews", required=True, help="Path to classified JSON input")
    parser.add_argument("--issues", required=True, help="Path to top issues report JSON")
    parser.add_argument("--output", required=True, help="Path to final analytics JSON output")
    args = parser.parse_args()

    print(f"Generating detailed analytics from {args.reviews} and {args.issues}...")
    
    # We use a fixed "now" date to ensure trends are stable against our static dataset
    # In production, this would be datetime.now(timezone.utc)
    mock_now = datetime(2026, 4, 30, tzinfo=timezone.utc)
    
    results = run_analytics(args.reviews, args.issues, args.output, now_utc=mock_now)
    
    print(f"Analytics generated for {len(results)} sources. Saved to {args.output}")
    
    for source, analytics in results.items():
        print(f"\nAnalytics for {source}:")
        for issue in analytics:
            trend = issue['metrics']['trend_percentage']
            # Avoid unicode characters for Windows console compatibility
            dir_str = "UP" if trend > 0 else "DOWN" if trend < 0 else "STABLE"
            print(f"  {issue['title']}")
            print(f"    7d Trend: {dir_str} {abs(trend)}% (Total 30d: {issue['metrics']['total_mentions_30d']})")
            print(f"    Sentiment: {issue['metrics']['sentiment_distribution']}")

if __name__ == "__main__":
    main()
