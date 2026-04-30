from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    google_play_path = root / "google_play_reviews_clean.json"
    trustpilot_path = root / "one_time_playwright" / "trustpilot_reviews.json"
    output_path = Path(__file__).resolve().parent / "combined_input.json"

    google_play = json.loads(google_play_path.read_text(encoding="utf-8"))
    trustpilot_raw = json.loads(trustpilot_path.read_text(encoding="utf-8"))
    trustpilot_reviews = trustpilot_raw.get("reviews", [])

    combined: list[dict[str, str]] = []

    for item in google_play:
        text = str(item.get("text", "")).strip()
        if text:
            combined.append({"source": "google_play", "text": text})

    for item in trustpilot_reviews:
        text = str(item.get("text", "")).strip()
        if text:
            combined.append({"source": "trustpilot", "text": text})

    # Reddit sample/output (manual sample for combined Phase 2 run).
    reddit_sample = [
        {"source": "reddit", "text": "I keep hitting token limits in one short session."},
        {"source": "reddit", "text": "Claude skills are useful, but reliability varies by task."},
        {"source": "reddit", "text": "Compared to ChatGPT and Gemini, Claude gives better long-form reasoning."},
        {"source": "reddit", "text": "Model quality dropped this week with slower responses and more refusals."},
        {"source": "reddit", "text": "Support response is slow when account issues happen."},
    ]
    combined.extend(reddit_sample)

    output_path.write_text(json.dumps(combined, indent=2), encoding="utf-8")
    print(f"Saved {len(combined)} records to {output_path}")


if __name__ == "__main__":
    main()

