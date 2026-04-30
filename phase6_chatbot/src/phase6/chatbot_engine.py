import json
from openai import OpenAI
from typing import List, Dict

class ChatbotEngine:
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        self.model = model

    def query(self, user_question: str, context_data: List[Dict]) -> str:
        """Processes a user question using the provided context from analytics."""
        
        # Prepare context summary for the LLM
        context_str = "CONTEXT INFORMATION (Processed Reviews & Analytics):\n"
        for i, issue in enumerate(context_data[:10]): # Top 10 issues for context
            context_str += f"\nIssue: {issue.get('title')}\n"
            context_str += f"Theme: {issue.get('theme')}\n"
            context_str += f"Description: {issue.get('description')}\n"
            context_str += f"Mentions: {issue.get('metrics', {}).get('total_mentions_30d', 0)}\n"
            context_str += f"Sentiment: {issue.get('metrics', {}).get('avg_sentiment', 0)}\n"
            context_str += "Evidence Snippets:\n"
            for snippet in issue.get('evidence', [])[:3]:
                context_str += f"- {snippet}\n"

        system_prompt = f"""
        You are 'Claude Review Intelligence Assistant', an expert NLP analyst.
        Your goal is to answer user questions about Claude review data based ONLY on the provided context.
        
        RULES:
        1. Base your answers strictly on the context provided.
        2. If the context doesn't contain the answer, say "I don't have enough data to answer that specifically."
        3. ALWAYS cite the specific issue or theme you are referencing.
        4. Do NOT mention any PII (Usernames, emails, links) in your response.
        5. Use a professional, analytical tone.
        
        {context_str}
        """

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question},
                ],
                temperature=0.3
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error communicating with Grok API: {str(e)}"

def load_analytics_context(source: str) -> List[Dict]:
    try:
        with open("phase4_analytics.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get(source, [])
    except:
        return []
