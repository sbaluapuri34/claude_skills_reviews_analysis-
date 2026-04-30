# One-time Playwright Scraper

Minimal manual script:
- opens a URL
- extracts review-like text
- saves JSON

## Run

1. Install Playwright in this folder:
   - `npm init -y`
   - `npm install playwright`
2. Run:
   - `node scrape_reviews.js "https://uk.trustpilot.com/review/claude.ai" trustpilot_reviews.json`
   - `node scrape_reviews.js "https://www.g2.com/products/claude-2025-12-11/reviews#reviews" g2_reviews.json`
   - `node scrape_reviews.js "https://play.google.com/store/apps/details?id=com.anthropic.claude&hl=en&pli=1" playstore_reviews.json`

