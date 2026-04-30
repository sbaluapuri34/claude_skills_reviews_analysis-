# Claude Review Intelligence Platform

An end-to-end NLP platform for analyzing user feedback across Reddit, Google Play, and Trustpilot. It identifies major themes, tracks trends, and provides a Grok-powered RAG chatbot for conversational analysis.

## 🚀 Features
- **Automated Ingestion**: Live fetching from `r/ClaudeAI`, `r/claude`, and `r/claudeskills`.
- **Advanced Preprocessing**: Strict PII redaction and one-word review filtering.
- **Granular Classification**: Categorizes reviews into 8+ descriptive themes (Skills, Tokens, Performance).
- **Trend Analytics**: 7-day and 30-day trend detection with sentiment distribution.
- **Interactive Dashboard**: Streamlit UI with data visualizations and PDF/Markdown report export.
- **RAG Chatbot**: Powered by **xAI Grok-beta** to answer questions based on review data.

## 🛠️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/your-username/claude-review-intelligence.git
cd claude-review-intelligence
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory:
```bash
XAI_API_KEY=your_grok_api_key_here
```

### 4. Run the Pipeline
Execute the master pipeline to fetch and process data:
```bash
python main.py
```

### 5. Launch the Dashboard
Start the Streamlit UI:
```bash
./run_dashboard.ps1
# OR
python -m streamlit run phase5_ui_report/app.py
```

## 📂 Project Structure
- `phase2_preprocessing/`: Ingestion and PII redaction logic.
- `phase3_classification/`: NLP theme engine and issue mining.
- `phase4_analytics/`: Trend detection and reporting.
- `phase5_ui_report/`: Streamlit dashboard and report generator.
- `phase6_chatbot/`: Grok-beta RAG integration.
- `main.py`: End-to-end orchestration.

## 🔒 Safety & Privacy
This platform implements a **Zero-PII policy**. All usernames, links, and emails are redacted before any data is stored or processed by the LLM.

---
*Built with ❤️ for the Claude Community.*
