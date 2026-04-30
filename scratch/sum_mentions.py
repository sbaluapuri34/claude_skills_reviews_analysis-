import json

with open('phase4_analytics.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for source, issues in data.items():
    total_mentions = sum(i['metrics']['total_mentions_30d'] for i in issues)
    print(f"Source: {source} | Total Mentions in Top 7: {total_mentions}")
