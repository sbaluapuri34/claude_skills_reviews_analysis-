import pytest
from phase5.report_generator import ReportGenerator

def test_report_generation():
    mock_data = {
        "test_source": [
            {
                "issue_id": "test_issue",
                "theme": "Test Theme",
                "title": "Descriptive Title",
                "description": "Detailed description",
                "metrics": {
                    "total_mentions_30d": 10,
                    "avg_sentiment": -0.5,
                    "trend_percentage": 50.0
                },
                "evidence": ["Evidence 1", "Evidence 2"]
            }
        ]
    }
    
    generator = ReportGenerator(mock_data)
    markdown = generator.generate_markdown_report("test_source")
    
    assert "# Review Intelligence Report: test_source" in markdown
    assert "Descriptive Title" in markdown
    assert "Evidence 1" in markdown
    assert "+50.0%" in markdown

def test_invalid_source():
    generator = ReportGenerator({})
    markdown = generator.generate_markdown_report("invalid")
    assert "not found" in markdown
