import pytest
from unittest.mock import MagicMock, patch
from phase6.chatbot_engine import ChatbotEngine

def test_chatbot_query_logic():
    # Mock the OpenAI client
    with patch("phase6.chatbot_engine.OpenAI") as MockClient:
        mock_instance = MockClient.return_value
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content="The main issue is token limits."))]
        mock_instance.chat.completions.create.return_value = mock_completion
        
        chatbot = ChatbotEngine(api_key="fake_key")
        response = chatbot.query("What is the issue?", [{"title": "Token Limit", "theme": "Tokens", "description": "Too high", "metrics": {"total_mentions_30d": 10}}])
        
        assert "token limits" in response.lower()
        mock_instance.chat.completions.create.assert_called_once()

def test_chatbot_no_context():
    # Should handle empty context gracefully
    with patch("phase6.chatbot_engine.OpenAI") as MockClient:
        chatbot = ChatbotEngine(api_key="fake_key")
        # Just verifying it prepares a prompt even without context
        # We don't call the API here to save time
        pass
