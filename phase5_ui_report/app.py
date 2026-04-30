import streamlit as st
import json
import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from phase5.report_generator import ReportGenerator
from phase6.chatbot_engine import ChatbotEngine, load_analytics_context

load_dotenv() # Load local .env file if it exists

st.set_page_config(page_title="Claude Review Intelligence", layout="wide")

st.title("🚀 Claude Review Intelligence Dashboard")
st.markdown("Analyzing user feedback across Reddit, Google Play, and Trustpilot.")

# Load Data
@st.cache_data
def load_data():
    analytics_path = Path("phase4_analytics.json")
    if analytics_path.exists():
        with open(analytics_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

data = load_data()

if not data:
    st.error("No analytics data found. Please run Phase 4 first.")
    st.stop()

# Sidebar - Source Selection
sources = list(data.keys())
selected_source = st.sidebar.selectbox("Select Review Source", sources)

# Main Dashboard
st.header(f"Insights for {selected_source}")

issues = data[selected_source]

# Metrics Row
col1, col2, col3 = st.columns(3)
col1.metric("Top Issues Identified", len(issues))
total_mentions = sum(i['metrics']['total_mentions_30d'] for i in issues)
col2.metric("Total Mentions (30d)", total_mentions)
avg_sentiment = sum(i['metrics']['avg_sentiment'] for i in issues) / len(issues)
col3.metric("Global Sentiment", round(avg_sentiment, 2))

st.divider()

# Issues Table
st.subheader("Major Issues & Trends")
df_data = []
for i in issues:
    df_data.append({
        "Issue": i['title'],
        "Mentions": i['metrics']['total_mentions_30d'],
        "Trend": f"{i['metrics']['trend_percentage']}%",
        "Sentiment": i['metrics']['avg_sentiment']
    })
st.table(pd.DataFrame(df_data))

# Detailed View
st.subheader("Issue Deep Dive")
for i in issues:
    with st.expander(f"🔍 {i['title']} ({i['metrics']['total_mentions_30d']} mentions)"):
        st.write(f"**Theme**: {i['theme']}")
        st.write(i['description'])
        st.write("**Sentiment Distribution**")
        st.bar_chart(i['metrics']['sentiment_distribution'])
        st.write("**Evidence Snippets**")
        for snippet in i['evidence']:
            st.info(f"\"{snippet}\"")

# Report Generation
st.divider()
st.subheader("📄 Export Detailed Report")
if st.button(f"Generate PDF Report for {selected_source}"):
    generator = ReportGenerator(data)
    report_path = f"{selected_source.replace('/', '_')}_report.md"
    generator.save_report(selected_source, report_path)
    st.success(f"Report generated: {report_path}")
    st.markdown("*(Note: In production, this Markdown is converted to PDF using WeasyPrint)*")
    with open(report_path, "rb") as f:
        st.download_button("Download Markdown Report", f, file_name=report_path)

# --- NEW: Phase 6 Analysis Chatbot ---
st.divider()
st.subheader("🤖 Analysis Chatbot (Beta)")
st.info("Ask questions like: 'What are the main complaints about tokens?' or 'Summarize the autonomy issues on Reddit.'")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask about the reviews..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # API Key from environment variable (for GitHub safety)
        api_key = os.getenv("XAI_API_KEY") 
        
        if not api_key:
            st.error("XAI_API_KEY not found in environment. Please set it in your .env file.")
            st.stop()
        
        context = load_analytics_context(selected_source)
        chatbot = ChatbotEngine(api_key=api_key)
        
        with st.spinner("Analyzing data with Grok..."):
            response = chatbot.query(prompt, context)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
