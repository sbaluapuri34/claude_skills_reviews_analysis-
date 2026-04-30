import json

with open('reddit_classified.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

keywords = ['context', 'writing', 'report', 'business', 'non-tech', 'non-technical', 'formatting', 'cowork']
non_tech_reviews = []

for item in data:
    text = item['text'].lower()
    if any(kw in text for kw in keywords) and 'Other' not in item['themes']:
        non_tech_reviews.append(item)

for i, item in enumerate(non_tech_reviews[:15]):
    print(f"--- Review {i+1} ---")
    print(f"Themes: {item['themes']}")
    print(f"Text: {item['text'][:500]}...")
    print("\n")
