import streamlit as st
import json
import os
import pandas as pd
import sys
from pathlib import Path
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# Add all phase source directories to sys.path so they can be imported
root_dir = Path(__file__).parent
sys.path.append(str(root_dir / "phase2_preprocessing" / "src"))
sys.path.append(str(root_dir / "phase3_classification" / "src"))
sys.path.append(str(root_dir / "phase4_analytics" / "src"))
sys.path.append(str(root_dir / "phase5_ui_report" / "src"))
sys.path.append(str(root_dir / "phase6_chatbot" / "src"))

from phase5.report_generator import ReportGenerator
from phase6.chatbot_engine import ChatbotEngine, load_analytics_context

if load_dotenv:
    load_dotenv() 

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
    st.error("No analytics data found. Please run the master pipeline (main.py) to generate data.")
    st.stop()

# Sidebar - Source & Model Selection
sources = list(data.keys())
selected_source = st.sidebar.selectbox("Select Review Source", sources)

st.sidebar.divider()
selected_model = st.sidebar.selectbox(
    "Select Model (Groq)", 
    ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
    index=0
)
debug_mode = st.sidebar.checkbox("Enable Debug Mode")

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

# --- Phase 6 Analysis Chatbot ---
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
        # Check environment variables then Streamlit secrets
        api_key = os.getenv("XAI_API_KEY") or st.secrets.get("XAI_API_KEY")
        
        if not api_key:
            st.error("XAI_API_KEY not found. Please ensure it is set in 'Settings > Secrets' on Streamlit Cloud.")
            st.stop()
        
        context = load_analytics_context(selected_source)
        chatbot = ChatbotEngine(api_key=api_key, model=selected_model)
        
        with st.spinner(f"Analyzing data with {selected_model}..."):
            response = chatbot.query(prompt, context)
            if "Error communicating" in response and debug_mode:
                st.error(f"DEBUG INFO: {response}")
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
