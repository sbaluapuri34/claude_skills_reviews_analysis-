# Phase 0 Discovery Artifacts

This folder implements Phase 0 from `SYSTEM_ARCHITECTURE.md`.

## Included artifacts

- `data/source_compliance_matrix.json`: source-level access/compliance contract.
- `data/canonical_schema.json`: normalized review schema contract with no-PII constraints.
- `data/theme_taxonomy.json`: initial theme taxonomy for downstream classification.
- `src/phase0/validators.py`: contract validators.
- `tests/test_phase0_validation.py`: automated test ensuring Phase 0 artifacts are valid.

## Run tests

1. Create and activate a virtual environment (recommended).
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Run:
   - `python -m pytest -q`

