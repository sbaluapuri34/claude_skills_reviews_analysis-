import json
import argparse
from pathlib import Path
from phase3.classifier import process_reviews, mine_top_issues

def main():
    parser = argparse.ArgumentParser(description="Run Phase 3: Theme Classification and Issue Mining.")
    parser.add_argument("--input", required=True, help="Path to preprocessed JSON input")
    parser.add_argument("--output", required=True, help="Path to classified JSON output")
    parser.add_argument("--report", required=True, help="Path to top issues report JSON")
    args = parser.parse_args()

    print(f"Loading data from {args.input}...")
    classified_data = process_reviews(args.input, args.output)
    print(f"Classified {len(classified_data)} reviews. Saved to {args.output}")

    print("Mining top issues...")
    top_issues = mine_top_issues(classified_data)
    
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(top_issues, f, indent=2, ensure_ascii=False)
        
    print(f"Top issues report saved to {args.report}")
    
    # Print summary to console
    for source, issues in top_issues.items():
        print(f"\nTop Issues for {source}:")
        for i, issue in enumerate(issues, 1):
            title = issue['descriptive_title']
            mentions = issue['metrics']['mentions']
            sentiment = issue['metrics']['avg_sentiment']
            print(f"  {i}. {title}")
            print(f"     (Theme: {issue['theme']}, Mentions: {mentions}, Sentiment: {sentiment})")

if __name__ == "__main__":
    main()
