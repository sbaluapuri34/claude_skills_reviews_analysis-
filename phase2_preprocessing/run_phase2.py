from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import argparse

from phase2.preprocess import run_phase2


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Phase 2 preprocessing.")
    parser.add_argument("--input", required=True, help="Input JSON path")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    count = run_phase2(
        Path(args.input),
        Path(args.output),
        now_utc=datetime.now(timezone.utc),
    )
    print(f"Saved {count} preprocessed reviews to {args.output}")


if __name__ == "__main__":
    main()

