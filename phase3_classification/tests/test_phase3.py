import pytest
from phase3.classifier import ReviewClassifier, mine_top_issues

def test_classification():
    classifier = ReviewClassifier()
    
    # Test token limit
    assert "Token Limits & Usage Caps" in classifier.classify("I reached my message limit for the day.")
    
    # Test competitor
    assert "Competitor Comparison" in classifier.classify("ChatGPT is better than Claude.")
    
    # Test multiple
    themes = classifier.classify("The UI has a bug and the model is lazy.")
    assert "UX & Stability" in themes
    assert "Model Quality & Intelligence" in themes

def test_sentiment_mock():
    classifier = ReviewClassifier()
    assert classifier.calculate_sentiment_mock("This is amazing and helpful") > 0
    assert classifier.calculate_sentiment_mock("This is bad and a problem") < 0

def test_issue_mining():
    classified_reviews = [
        {"source": "test", "themes": ["UX & Stability"], "sentiment_score": -0.5, "text": "UI is bad"},
        {"source": "test", "themes": ["UX & Stability"], "sentiment_score": -0.7, "text": "App crashed"},
        {"source": "test", "themes": ["Model Quality & Intelligence"], "sentiment_score": 0.5, "text": "Smart model"},
    ]
    
    report = mine_top_issues(classified_reviews)
    assert "test" in report
    assert report["test"][0]["theme"] == "UX & Stability" # Most mentions + negative sentiment
    assert report["test"][0]["count"] == 2
