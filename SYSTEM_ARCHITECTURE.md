# System Architecture: 30-Day Multi-Source Review Intelligence Platform

## 1) Objective

Build a platform that:
- Collects reviews/posts from the last 30 days from:
  - `https://uk.trustpilot.com/review/claude.ai`
  - `https://play.google.com/store/apps/details?id=com.anthropic.claude&hl=en&pli=1`
  - `https://www.reddit.com/r/ClaudeAI/`
  - `https://www.reddit.com/r/claude/`
  - `https://www.reddit.com/r/claudeskills/`
  - `https://www.g2.com/products/claude-2025-12-11/reviews#reviews`
- Ignores one-word reviews/posts.
- Performs NLP-based thematic classification (examples: token usage limits, skills quality, competitor comparisons, model quality/issues).
- Selects top 7 issues/themes per source.
- Displays insights in UI and generates detailed per-source PDF reports on CTA click.
- Includes a chatbot that answers user questions about findings, trends, themes, and evidence.

---

## 2) Architecture Principles

- **Compliance-first ingestion:** Use official APIs where available (Reddit API, Google Play data providers if licensed) and respect robots.txt/ToS.
- **Deterministic + AI hybrid analysis:** Combine rule-based tagging and LLM classification for stable output.
- **Traceability:** Every issue in report must link back to source review IDs/URLs.
- **Incremental processing:** Daily jobs process deltas; no full reprocessing by default.
- **Source isolation:** Each source has dedicated adapter and parsing logic.
- **Zero-PII policy:** Do not store, expose, or return personally identifiable information at any stage.
- **Safe-by-default execution:** Phase 1 enables only API-safe sources; scraping paths are blocked.

---

## 3) High-Level Components

1. **Source Connectors (Ingestion Layer)**
   - Trustpilot Connector
   - Google Play Connector
   - Reddit Connector (multi-subreddit)
   - G2 Connector

2. **Raw Data Store**
   - Stores source payloads only after PII redaction + metadata (ingestion timestamp, source, URL, anonymized author token).

3. **Normalization & Quality Layer**
   - Canonical schema mapping.
   - Language detection.
   - One-word filtering.
   - De-duplication.
   - Date-window filter (last 30 days).

4. **Analytics & Theme Engine**
   - Sentiment scoring.
   - Theme classification (multi-label).
   - Topic clustering.
   - Issue ranking model to compute top 7 issues/source.

5. **Report Service**
   - On-demand PDF generation.
   - Per-source detailed breakdown of top 7 issues.
   - Evidence snippets and trend charts.

6. **UI + API Gateway**
   - Dashboard cards by source.
   - CTA button: “Generate Detailed PDF”.
   - Job status + secure file download.

7. **Analysis Chatbot Service**
   - Conversational Q&A over processed analytics data.
   - Retrieval from issue summaries, evidence snippets, and trend metrics.
   - Source-cited answers with guardrails for unsupported claims.

8. **Orchestration & Observability**
   - Scheduler/workflows.
   - Retries and dead-letter queues.
   - Metrics, logs, alerting.

---

## 4) Phased Architecture Plan

## Source Capability Matrix (Control Plane)

Every source must declare:
- `access_type`: `API | partner_api | scraping | unsupported`
- `compliance_level`: `safe | restricted | high-risk`
- `enabled_by_default`: boolean
- `requires_api_key`: boolean

Initial matrix:
- `reddit_claudeai`: `API`, `safe`, enabled by default, API key required.
- `reddit_claude`: `API`, `safe`, enabled by default, API key required.
- `reddit_claudeskills`: `API`, `safe`, enabled by default, API key required.
- `trustpilot_claude_ai`: `scraping`, `high-risk`, disabled by default.
- `g2_claude_reviews`: `scraping`, `high-risk`, disabled by default.
- `google_play_claude`: `partner_api`, `restricted`, disabled by default.

One-time Playwright policy:
- Trustpilot, G2, and Google Play may use a **manual one-time Playwright backfill script**.
- This path is disabled by default and treated as restricted/high-risk operation.
- This path is never auto-scheduled in Phase 1.

## Phase 0: Discovery, Legal, and Data Contracts

**Goals**
- Validate allowed data access for each source.
- Define canonical review schema and taxonomy.

**Outputs**
- Source compliance matrix (API vs scraping path).
- Canonical schema:
  - `source`
  - `source_review_id`
  - `source_url`
  - `author_id_hash`
  - `rating` (nullable)
  - `title` (nullable)
  - `body_text`
  - `created_at_utc`
  - `ingested_at_utc`
  - `language`
  - `is_one_word`
  - `dedupe_key`
- Initial theme dictionary and examples.

---

## Phase 1: Ingestion MVP (Source Adapters)

**Goals**
- Implement Reddit ingestion only using official API.
- Keep Trustpilot, G2, and Google Play as stub adapters only.
- Store raw and normalized records for enabled safe sources.
- Optionally support one-time manual Playwright backfill workflow for non-API sources (disabled by default).

**Design**
- Build adapter interface:
  - `fetch_since(source_config, since_datetime_utc) -> List[RawItem]`
- Implement adapter types:
  - `ApiAdapter` for safe API sources.
  - `ScrapingAdapter` for restricted/high-risk sources (disabled by default, no Phase 1 execution).
  - `StubAdapter` for placeholders/future sources.
  - `OneTimePlaywrightStubAdapter` for manual backfill control-plane wiring only.
- Implement source adapters for Phase 1:
  - Reddit: official API adapter for `r/ClaudeAI`, `r/claude`, `r/claudeskills`.
  - Trustpilot/G2/Google Play: stub adapters that return no data.
- Persist raw payloads in object storage (JSON).
- Persist normalized records in relational DB.

**Controls**
- Feature flags:
  - `ENABLE_REDDIT_INGESTION=true`
  - `ENABLE_TRUSTPILOT_INGESTION=false`
  - `ENABLE_G2_INGESTION=false`
  - `ENABLE_GOOGLE_PLAY_INGESTION=false`
  - `ENABLE_ONE_TIME_PLAYWRIGHT_BACKFILL=false`
- Safe mode:
  - `SAFE_MODE=true` by default.
  - In safe mode, block all non-API adapters.
- Compliance gate:
  - Block sources where `compliance_level != safe`.
  - Allow override only through environment flag.
- Adapter budget guards (required per adapter):
  - `max_requests_per_minute`
  - `max_requests_per_day`
  - `max_items_per_run`
- Backoff and retry.
- Source-specific parser validation tests.
- Cost and usage telemetry per run:
  - `api_calls_used`
  - `estimated_cost`
  - `records_fetched`

**One-time Playwright execution conditions**
- Manual trigger only (never default or scheduled).
- Requires all of:
  - `ENABLE_ONE_TIME_PLAYWRIGHT_BACKFILL=true`
  - source-specific feature flag enabled
  - `SAFE_MODE=false`
  - compliance override env flag enabled
- No scraping logic is part of core ingestion runtime in Phase 1.

---

## Phase 2: Data Quality & Preprocessing

**Goals**
- Prepare clean analysis-ready dataset.

**Core Rules**
- Keep only records where `created_at_utc >= now() - 30 days`.
- Ignore one-word reviews:
  - Tokenize on whitespace.
  - If token count == 1, set `is_one_word=true` and exclude from analysis.
- PII handling (strict):
  - Remove usernames, emails, phone numbers, profile links, and free-text PII patterns before storage.
  - Do not persist raw author handles; use anonymized, non-reversible internal IDs only when required for dedupe.
  - Exclude any review from evidence snippets if redaction confidence is low.
- Remove duplicates:
  - Exact text hash + fuzzy near-duplicate threshold.
- Normalize text:
  - Strip HTML, normalize unicode, lowercasing for features (keep raw copy).
- Language filtering:
  - Process English first; route others for future multilingual phase.

---

## Phase 3: Theme Classification and Issue Mining

**Goals**
- Assign meaningful themes and identify top 7 issues per source.

**Classification Strategy**
- **Layer A: Rule-based tags**
  - Keyword/phrase dictionaries for deterministic tagging:
    - Token limits/usage caps
    - Claude Skills quality/usability
    - Comparisons vs ChatGPT/Gemini/Microsoft Copilot
    - Model quality (hallucinations, refusals, latency, regressions)
    - Pricing/credits
    - App stability/UX
    - Support & trust concerns
- **Layer B: Grok classifier**
  - Multi-label theme assignment + confidence score.
- **Layer C: Topic clustering**
  - Embedding-based clustering for emerging themes not in dictionary.

**Issue Ranking Formula (per source)**
- `issue_score = volume_weight * mention_count + sentiment_weight * negative_intensity + recency_weight * recent_mentions + engagement_weight * helpful_votes_or_upvotes`
- Select top 7 by score.

**Output Tables**
- `review_theme_map`
- `issue_summary_by_source`
- `issue_evidence`

---

## Phase 4: Detailed Analytics Layer

**Goals**
- Create explainable issue insights for each source.

**For each of top 7 issues/source, compute**
- Total mentions.
- Negative/neutral/positive split.
- 7-day and 30-day trend.
- Representative evidence snippets (3-10 quotes).
- Optional competitor mention breakdown (ChatGPT/Gemini/Microsoft).
- Confidence and data quality notes.

**Explainability**
- Every issue detail includes:
  - Theme definition.
  - Why selected in top 7.
  - Linked source URLs/IDs (traceability).

---

## Phase 5: UI and CTA-Driven PDF Generation

**Goals**
- Deliver user-facing dashboards + exportable detailed reports.

**UI Flow**
1. User selects source (or all sources).
2. User clicks CTA: `Generate Detailed PDF`.
3. Frontend calls `POST /reports/generate`.
4. Backend creates async report job.
5. User sees status (`queued -> running -> ready`).
6. User downloads PDF from signed URL.

**PDF Structure (per source)**
- Executive summary.
- Top 7 issues list with scores.
- Detailed section for each issue:
  - Description
  - Metrics
  - Evidence excerpts
  - Trend visualization
  - Recommended action cues
- Appendix:
  - Methodology
  - Filtering policy (one-word excluded)
  - Source coverage and timestamp range.

---

## Phase 6: Analysis Chatbot (RAG + Guardrails)

**Goals**
- Allow users to ask natural-language questions about analysis results.

**Chatbot Capabilities**
- Answer questions such as:
  - "What are the top complaints on Google Play this month?"
  - "How often are token limits mentioned vs model quality issues?"
  - "Show evidence for competitor comparisons on Reddit."
- Return grounded answers with:
  - Issue metrics
  - Trend deltas
  - Evidence snippets + source links

**Technical Design**
- Retrieval index built from:
  - `issue_summary_by_source`
  - `issue_evidence`
  - `issue_metrics_daily`
  - `reviews_normalized` (filtered and deduped)
- RAG pipeline:
  1. Query understanding and intent classification.
  2. Structured retrieval (SQL) + semantic retrieval (vector index).
  3. LLM answer generation with citations.
  4. Post-check: reject unsupported statements and prompt re-query if needed.

**Guardrails**
- No answer without citation-backed evidence.
- Clearly mark low-confidence responses.
- Restrict responses to configured date window (default last 30 days).
- Enforce source-level filters when user asks for a specific site.
- Never return PII; redact sensitive spans in all chatbot outputs.

---

## Phase 7: Production Hardening and Governance

**Goals**
- Make system reliable, auditable, and scalable.

**Hardening**
- Workflow orchestrator with idempotent jobs.
- Dead-letter queues for failed source fetches.
- Backfill utility for missed days.
- Caching for repeated PDF requests with same date window.

**Governance**
- No-PII storage and output policy enforcement.
- Data retention policy per source.
- Audit logs for generated reports.
- Versioned taxonomy for consistent historical analytics.

---

## 5) Reference Technical Stack (Suggested)

- **Backend:** Python (FastAPI) or Node.js (NestJS)
- **Ingestion/Scheduling:** Airflow or Temporal + message queue
- **Storage:**
  - Raw payloads: S3-compatible object store
  - Normalized/analytics: PostgreSQL
  - Search/semantic: OpenSearch (optional)
- **NLP/ML:**
  - Embeddings + clustering (e.g., sentence-transformers)
  - Grok model for multi-label theme classification
- **Chatbot/RAG:**
  - Vector store (pgvector/OpenSearch)
  - Grok-based response orchestration with citation grounding
- **Frontend:** React + charting library
- **PDF:** WeasyPrint / Playwright-based HTML-to-PDF
- **Observability:** OpenTelemetry + Prometheus + Grafana

---

## 6) Canonical Data Model (Core Entities)

- `sources`
- `raw_items`
- `reviews_normalized`
- `themes`
- `review_theme_map`
- `issues`
- `issue_metrics_daily`
- `report_jobs`
- `report_artifacts`
- `chat_sessions`
- `chat_messages`
- `chat_citations`

Key relation: one normalized review can map to multiple themes (many-to-many).
All entities store redacted text and non-PII metadata only.

---

## 7) API Contract (Minimal)

- `POST /ingestion/run?source=<id>&since=<iso8601>`
- `GET /issues?source=<id>&window_days=30`
- `GET /issues/<issue_id>/details`
- `POST /reports/generate`  
  Request: `{ source_id, window_days: 30, format: "pdf" }`
- `GET /reports/<job_id>/status`
- `GET /reports/<job_id>/download`
- `POST /chat/query`  
  Request: `{ question, source_id?: string, window_days?: number }`
- `GET /chat/sessions/<session_id>/history`

---

## 8) Non-Functional Requirements

- **Freshness:** Daily scheduled ingestion + on-demand refresh.
- **Latency:** PDF generation under 60-120s for single-source report.
- **Latency (chat):** Typical chatbot response under 5-10s.
- **Reliability:** 99% successful daily pipeline runs.
- **Scalability:** Add new review sources via adapter pattern.
- **Security:** Signed URLs, role-based access, encrypted data at rest/in transit.
- **Privacy:** Strict no-PII ingestion, storage, analytics, report, and chatbot response policy.
- **Compliance:** Non-safe sources are blocked by default and require explicit override.

---

## 9) Validation and Acceptance Criteria

- Phase 1 ingests and normalizes data from Reddit only (official API path).
- Trustpilot, G2, and Google Play remain non-fetching stubs in Phase 1.
- If one-time Playwright mode is not explicitly enabled, scraping sources must be blocked.
- Only reviews/posts from last 30 days are included.
- One-word reviews are excluded from analysis and reports.
- Safe mode blocks scraping adapters at runtime.
- Compliance gate blocks sources with `compliance_level != safe` unless override flag is enabled.
- Exactly top 7 issues are produced per source (if enough data exists; else return available count with warning).
- PDF is generated only when user clicks CTA and contains:
  - Top issues,
  - Detailed analysis per issue,
  - Evidence snippets,
  - Methodology/filter notes.
- Chatbot answers are citation-grounded and limited to available analysis data.
- Chatbot respects one-word review exclusion and 30-day window constraints in responses.
- Reports and chatbot responses contain no PII (validated redaction checks).

---

## 10) Risks and Mitigations

- **Source anti-bot/rate restrictions:** Prefer APIs, queue + retry + throttling.
- **Taxonomy drift over time:** Versioned theme sets and monthly review.
- **LLM inconsistency:** Hybrid deterministic+LLM approach and confidence thresholds.
- **Grok output inconsistency:** Hybrid deterministic+Grok approach and confidence thresholds.
- **Sparse data for some sources:** Fallback reporting with minimum sample disclaimers.
- **Chatbot hallucination risk:** Enforce retrieval-only grounding + citation validation.
- **PII leakage risk:** Multi-stage redaction + response-time PII scanners + block-on-detect policy.

---

## 11) Immediate Next Build Steps

1. Implement canonical schema and DB migrations.
2. Build Reddit adapter first (fastest API path), then Trustpilot and Google Play, then G2.
3. Implement preprocessing filters (30-day + one-word exclusion).
4. Build baseline issue ranking and top-7 selector.
5. Add UI CTA and async PDF generation pipeline.
6. Add chatbot API (`/chat/query`) with citation-aware RAG responses.
7. Add observability dashboards and source health alerts.
