from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ValidationResult:
    ok: bool
    message: str


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_compliance_matrix(path: Path) -> ValidationResult:
    data = _load_json(path)
    sources = data.get("sources", [])
    if not sources:
        return ValidationResult(False, "Compliance matrix must include at least one source.")

    required_fields = {
        "source_id",
        "url",
        "preferred_access",
        "fallback_access",
        "requires_legal_review",
        "status",
    }
    for source in sources:
        missing = required_fields - source.keys()
        if missing:
            return ValidationResult(False, f"Source entry missing fields: {sorted(missing)}")
    return ValidationResult(True, "Compliance matrix is valid.")


def validate_canonical_schema(path: Path) -> ValidationResult:
    data = _load_json(path)
    required_fields = data.get("required_fields", [])
    expected = {
        "source",
        "source_review_id",
        "source_url",
        "author_id_hash",
        "body_text",
        "created_at_utc",
        "ingested_at_utc",
        "language",
        "is_one_word",
        "dedupe_key",
    }
    if set(required_fields) != expected:
        return ValidationResult(False, "Canonical schema required_fields do not match expected contract.")

    constraints = data.get("constraints", {})
    if "author_id_hash" not in constraints or "body_text" not in constraints:
        return ValidationResult(False, "Canonical schema must enforce no-PII constraints.")
    return ValidationResult(True, "Canonical schema is valid.")


def validate_theme_taxonomy(path: Path) -> ValidationResult:
    data = _load_json(path)
    themes = data.get("themes", [])
    if len(themes) < 7:
        return ValidationResult(False, "Theme taxonomy must define at least 7 themes.")

    seen_ids: set[str] = set()
    for theme in themes:
        theme_id = theme.get("id")
        if not theme_id:
            return ValidationResult(False, "Theme is missing id.")
        if theme_id in seen_ids:
            return ValidationResult(False, f"Duplicate theme id found: {theme_id}")
        seen_ids.add(theme_id)
        if not theme.get("seed_keywords"):
            return ValidationResult(False, f"Theme '{theme_id}' must include seed_keywords.")
    return ValidationResult(True, "Theme taxonomy is valid.")


def validate_phase0(data_dir: Path) -> list[ValidationResult]:
    return [
        validate_compliance_matrix(data_dir / "source_compliance_matrix.json"),
        validate_canonical_schema(data_dir / "canonical_schema.json"),
        validate_theme_taxonomy(data_dir / "theme_taxonomy.json"),
    ]

