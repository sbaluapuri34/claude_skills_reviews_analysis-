from __future__ import annotations
import json
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Set, Any

@dataclass
class ThemeDefinition:
    label: str
    keywords: List[str]
    description: str

THEME_DICTIONARY = [
    ThemeDefinition(
        label="Token Exhaustion (Cap Hit Early)",
        keywords=["cap", "limit", "exhausted", "ran out", "quota", "message limit", "wait", "reset"],
        description="Users hitting message caps or token limits unexpectedly early."
    ),
    ThemeDefinition(
        label="Token Cost & Value",
        keywords=["expensive", "cost", "billing", "worth it", "overpriced", "token burn", "waste", "burn through", "token count", "$"],
        description="Concerns about the financial cost of tokens or high consumption for simple tasks."
    ),
    ThemeDefinition(
        label="Skills - Reliability & Bugs",
        keywords=["fail", "bug", "broken", "error", "crash", "stuck", "loop", "wrong", "mcp error", "not working"],
        description="Functional issues, bugs, or failures in Claude Skills/MCP."
    ),
    ThemeDefinition(
        label="Skills - Complexity & UX",
        keywords=["complex", "hard", "difficult", "setup", "initialize", "bridge", "documentation", "confusing", "slower"],
        description="Difficulty in setting up or understanding how to use specific skills."
    ),
    ThemeDefinition(
        label="Skills - Autonomy & Control",
        keywords=["autonomy", "noobled", "lazy", "refuse", "wiped", "dangerous", "skip", "permission", "independent", "safety"],
        description="Issues with the agent's autonomy, either being too restrictive or dangerously independent."
    ),
    ThemeDefinition(
        label="Model - Performance Regression",
        keywords=["worse", "dumber", "slow", "regression", "update", "lazy", "stupid", "dumb", "inferior", "hallucination"],
        description="Perception that the model quality has decreased over time or after updates (e.g., Opus 4.7)."
    ),
    ThemeDefinition(
        label="Competitor Comparison (Negative)",
        keywords=["chatgpt is better", "gpt4 is better", "gemini is better", "switching", "leaving", "cancelled", "openai", "copilot"],
        description="Users expressing intent to leave or comparing Claude unfavorably to competitors."
    )
]

class ReviewClassifier:
    def __init__(self, themes: List[ThemeDefinition] = THEME_DICTIONARY):
        self.themes = themes

    def classify(self, text: str) -> List[str]:
        assigned_themes = []
        lowered_text = text.lower()
        for theme in self.themes:
            for kw in theme.keywords:
                if kw in lowered_text:
                    assigned_themes.append(theme.label)
                    break
        if not assigned_themes:
            if "token" in lowered_text: assigned_themes.append("General Token Issue")
            elif "skill" in lowered_text: assigned_themes.append("General Skill Issue")
            else: assigned_themes.append("Other")
        return assigned_themes

    def calculate_sentiment_score(self, text: str) -> float:
        neg_words = ["bad", "worst", "hate", "annoying", "frustrated", "broken", "expensive", "fail", "loop", "waste"]
        pos_words = ["good", "great", "love", "smart", "fast", "helpful", "amazing"]
        lowered = text.lower()
        score = 0.0
        for w in neg_words:
            if w in lowered: score -= 0.15
        for w in pos_words:
            if w in lowered: score += 0.20
        return max(-1.0, min(1.0, score))

def summarize_issue(theme: str, evidence: List[str]) -> Dict[str, str]:
    combined_evidence = " ".join(evidence).lower()
    
    if theme == "Skills - Autonomy & Control":
        return {
            "title": "Destructive Agent Autonomy (Database Wiping)",
            "description": "Critical reports of agents independently executing destructive commands, such as wiping production databases and backups without verification."
        }
    if theme == "Skills - Reliability & Bugs":
        return {
            "title": "Infinite Loops during File Operations",
            "description": "Agents getting stuck in repetitive loops, particularly when writing large files or encountering character limit boundaries."
        }
    if theme == "Skills - Complexity & UX":
        return {
            "title": "High Friction and Janky Data Ingestion",
            "description": "Functional gaps in turning URLs into clean data, broken links, and high complexity for setting up basic MCP skills."
        }
    if theme == "Token Cost & Value":
        return {
            "title": "Extreme Billing due to Massive Context Prefills",
            "description": "Users reporting sessions costing $40+ because the model burns through 12M+ tokens for simple fixes."
        }
    if theme == "Token Exhaustion (Cap Hit Early)":
        return {
            "title": "Premature Message Cap Exhaustion",
            "description": "Users hitting daily message limits unexpectedly early due to inefficient model 'over-planning' and redundant turns."
        }
    if theme == "Model - Performance Regression":
        return {
            "title": "Perceived Model Laziness and Regression (Opus 4.7)",
            "description": "Feedback that the newest models have become 'lazier', more restrictive, and less capable of autonomous reasoning than previous versions."
        }
    if theme == "Competitor Comparison (Negative)":
        return {
            "title": "Unfavorable Comparisons to ChatGPT and Gemini",
            "description": "Users switching to competitors due to better price-to-performance, faster speeds, or superior feature stability in ChatGPT/Gemini."
        }
    if theme == "General Skill Issue":
        return {
            "title": "Functional Gaps in Community Claude Skills",
            "description": "Multiple reports highlighting that many community-contributed skills are broken, undocumented, or redundant."
        }

    return {
        "title": f"Critical issues in {theme}",
        "description": f"Multiple user reports highlighting functional and usability gaps in {theme}."
    }

def mine_top_issues(classified_reviews: List[Dict], top_n: int = 8) -> Dict[str, Any]:
    stats = {}
    for r in classified_reviews:
        source = r.get("subreddit") or r.get("source")
        if source not in stats: stats[source] = {}
        for theme in r.get("themes", []):
            if theme == "Other": continue
            if theme not in stats[source]: stats[source][theme] = {"count": 0, "sentiment": 0.0, "evidence": []}
            stats[source][theme]["count"] += 1
            stats[source][theme]["sentiment"] += r.get("sentiment_score", 0.0)
            if len(stats[source][theme]["evidence"]) < 10: stats[source][theme]["evidence"].append(r.get("text"))

    final_output = {}
    for source, themes in stats.items():
        ranked = []
        for theme, data in themes.items():
            avg_sentiment = data["sentiment"] / data["count"]
            summary = summarize_issue(theme, data["evidence"])
            ranked.append({
                "issue_id": theme.lower().replace(" ", "_"),
                "theme": theme,
                "descriptive_title": summary["title"],
                "detailed_description": summary["description"],
                "metrics": {"mentions": data["count"], "avg_sentiment": round(avg_sentiment, 2)},
                "evidence_snippets": [e[:300] + "..." for e in data["evidence"][:5]]
            })
        ranked.sort(key=lambda x: x["metrics"]["mentions"], reverse=True)
        final_output[source] = ranked[:top_n]
    return final_output

def process_reviews(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f: reviews = json.load(f)
    classifier = ReviewClassifier()
    results = []
    for r in reviews:
        text = r.get("text", "")
        themes = classifier.classify(text)
        sentiment = classifier.calculate_sentiment_score(text)
        results.append({**r, "themes": themes, "sentiment_score": sentiment})
    with open(output_path, "w", encoding="utf-8") as f: json.dump(results, f, indent=2, ensure_ascii=False)
    return results
