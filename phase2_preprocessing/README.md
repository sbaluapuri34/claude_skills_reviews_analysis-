# Phase 2 Preprocessing

Simple Phase 2 implementation for:
- last 30 days filtering
- English-only filtering
- one-word review removal
- basic PII redaction (email/phone)
- text normalization
- deduplication

## Run

```powershell
$env:PYTHONPATH='src'
python run_phase2.py --input "../google_play_reviews_clean.json" --output "./phase2_output.json"
```

## Test

```powershell
$env:PYTHONPATH='src'
python -m pytest -q
```

