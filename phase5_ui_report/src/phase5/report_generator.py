from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime

class ReportGenerator:
    def __init__(self, analytics_data: Dict):
        self.data = analytics_data

    def generate_markdown_report(self, source: str) -> str:
        """Generates a detailed markdown report which can be converted to PDF."""
        if source not in self.data:
            return f"# Report for {source} not found."
        
        issues = self.data[source]
        report = f"# Review Intelligence Report: {source}\n"
        report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += "## Executive Summary\n"
        report += "This report analyzes recent user feedback to identify critical friction points. "
        report += f"A total of {len(issues)} major issues were identified for {source} based on 30-day review volume.\n\n"
        
        report += "## Top 7 Issues Overview\n"
        report += "| Issue | Mentions | Trend | Sentiment |\n"
        report += "| :--- | :--- | :--- | :--- |\n"
        for i in issues[:7]:
            trend = i['metrics']['trend_percentage']
            trend_str = f"+{trend}%" if trend > 0 else f"{trend}%"
            report += f"| {i['title']} | {i['metrics']['mentions']} | {trend_str} | {i['metrics']['avg_sentiment']} |\n"
        
        report += "\n---\n\n"
        
        for i, issue in enumerate(issues[:7], 1):
            report += f"### {i}. {issue['title']}\n"
            report += f"**Theme**: {issue['theme']}  \n"
            report += f"**Description**: {issue['detailed_description']}  \n"
            report += f"**Metrics**: {issue['metrics']['mentions']} mentions | {issue['metrics']['avg_sentiment']} avg sentiment  \n\n"
            
            report += "#### Evidence Snippets\n"
            for snippet in issue['evidence_snippets']:
                report += f"- \"{snippet.strip()}\"\n"
            report += "\n"
            
        report += "\n---\n**Methodology**: Analysis performed using automated theme classification and trend detection. One-word reviews excluded."
        
        return report

    def save_report(self, source: str, output_path: str):
        content = self.generate_markdown_report(source)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path
