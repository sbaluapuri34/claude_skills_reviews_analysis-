import json
import os

def generate_summary():
    input_path = 'phase4_analytics.json'
    output_path = 'phase4_analytics/major_issues_summary.txt'
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    summary = "MAJOR ISSUES ANALYSIS SUMMARY: CLAUDE & CLAUDE SKILLS\n"
    summary += "=" * 50 + "\n\n"

    for source, issues in data.items():
        summary += f"SOURCE: {source}\n"
        summary += "-" * 50 + "\n"
        
        # Filter for major concerns: Skills, Tokens, Competitors
        major_issues = [i for i in issues if any(k in i['theme'] for k in ['Skill', 'Token', 'Competitor'])]
        
        for i in major_issues:
            summary += f"\nISSUE: {i['title']}\n"
            summary += f"  Category:    {i['theme']}\n"
            summary += f"  Explanation: {i['description']}\n"
            summary += f"  Metrics:\n"
            summary += f"    - Mentions (30d):   {i['metrics']['total_mentions_30d']}\n"
            summary += f"    - 7-Day Trend:      {i['metrics']['trend_percentage']}%\n"
            summary += f"    - Sentiment Score:  {i['metrics']['avg_sentiment']} (-1.0 to 1.0)\n"
            summary += f"    - Distribution:     {i['metrics']['sentiment_distribution']}\n"
            summary += f"  Key Evidence:\n"
            for snippet in i['evidence']:
                summary += f"    > \"{snippet.strip()}\"\n"
            summary += "\n"
            
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"Summary written to {output_path}")

if __name__ == "__main__":
    generate_summary()
