# Phase 1 Ingestion MVP

This folder implements Phase 1 from the architecture:

- Connector interface (`fetch_since(...)`) with adapter typing
- Source Capability Matrix with compliance metadata
- Reddit-only API ingestion in Phase 1
- Non-Reddit sources as disabled stubs (no scraping execution)
- Raw + normalized artifact writing
- 30-day ingestion window filtering
- Basic PII redaction in normalized text
- Feature flags and safe mode execution guardrails
- Compliance gate and per-run usage/cost logging

## Structure

- `data/source_capability_matrix.json`: source access/compliance control plane
- `src/phase1/connectors.py`: `ApiAdapter`, `ScrapingAdapter`, `StubAdapter`, test adapter
- `src/phase1/capabilities.py`: in-code source capability matrix
- `src/phase1/config.py`: feature flags + safe mode
- `src/phase1/adapters.py`: Reddit API adapters + disabled stubs
- `src/phase1/models.py`: raw and normalized data models
- `src/phase1/storage.py`: JSONL storage writer
- `src/phase1/pipeline.py`: ingestion orchestration + compliance gate + budgets + run telemetry
- `tests/test_phase1_ingestion.py`: Phase 1 test case

## Run tests

1. `pip install -r requirements.txt`
2. PowerShell: `$env:PYTHONPATH='src'`
3. `python -m pytest -q`

## Default feature flags

- `ENABLE_REDDIT_INGESTION=true`
- `ENABLE_TRUSTPILOT_INGESTION=false`
- `ENABLE_G2_INGESTION=false`
- `ENABLE_GOOGLE_PLAY_INGESTION=false`
- `ENABLE_ONE_TIME_PLAYWRIGHT_BACKFILL=false`
- `SAFE_MODE=true`
- `ALLOW_NON_SAFE_SOURCES=false`

## One-time Playwright backfill (controlled)

- Allowed as a manual, one-time fallback for:
  - Trustpilot
  - G2
  - Google Play
- Must remain disabled by default.
- Requires explicit flags and still cannot run when `SAFE_MODE=true`.
- Scraping logic is intentionally not implemented in this repository.

