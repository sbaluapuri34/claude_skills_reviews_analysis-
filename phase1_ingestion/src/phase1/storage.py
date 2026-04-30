from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

from phase1.models import NormalizedReview, RawItem


def _json_default(value: object) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Unsupported type: {type(value)}")


class JsonlStorage:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.raw_dir = self.base_dir / "raw"
        self.normalized_dir = self.base_dir / "normalized"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.normalized_dir.mkdir(parents=True, exist_ok=True)

    def write_raw(self, source: str, items: Iterable[RawItem]) -> Path:
        path = self.raw_dir / f"{source}.jsonl"
        with path.open("w", encoding="utf-8") as file:
            for item in items:
                file.write(json.dumps(asdict(item), default=_json_default) + "\n")
        return path

    def write_normalized(self, source: str, items: Iterable[NormalizedReview]) -> Path:
        path = self.normalized_dir / f"{source}.jsonl"
        with path.open("w", encoding="utf-8") as file:
            for item in items:
                file.write(json.dumps(asdict(item), default=_json_default) + "\n")
        return path

    def write_run_log(self, run_log: dict[str, object]) -> Path:
        path = self.base_dir / "run_log.json"
        with path.open("w", encoding="utf-8") as file:
            file.write(json.dumps(run_log, indent=2, default=_json_default))
        return path

