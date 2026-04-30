const fs = require("fs");
const { chromium } = require("playwright");

async function scrape(url, outputPath) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: "networkidle", timeout: 60000 });

  // Wait for Trustpilot review cards to render (dynamic content).
  await page.waitForSelector("article[data-service-review-card-paper]", { timeout: 30000 });

  // Expand "Read more" buttons when present so full review text is visible.
  const readMoreButtons = page.locator("button", { hasText: /read more/i });
  const buttonCount = await readMoreButtons.count();
  for (let i = 0; i < buttonCount; i += 1) {
    try {
      await readMoreButtons.nth(i).click({ timeout: 1500 });
    } catch {
      // Ignore click failures; continue extracting visible text.
    }
  }

  // Extract visible review body text from Trustpilot review cards.
  const candidates = await page.$$eval(
    [
      "article[data-service-review-card-paper] p[data-service-review-text-typography]",
      "article[data-service-review-card-paper] [data-service-review-text-typography]",
      "article[data-service-review-card-paper] p"
    ].join(","),
    (nodes) =>
      nodes
        .filter((n) => {
          const style = window.getComputedStyle(n);
          const rect = n.getBoundingClientRect();
          return (
            style &&
            style.visibility !== "hidden" &&
            style.display !== "none" &&
            rect.width > 0 &&
            rect.height > 0
          );
        })
        .map((n) => (n.textContent || "").replace(/\s+/g, " ").trim())
        .filter((t) => t.length > 20)
  );

  const uniqueReviews = [...new Set(candidates)];
  const payload = {
    url,
    scraped_at_utc: new Date().toISOString(),
    total_reviews: uniqueReviews.length,
    reviews: uniqueReviews.map((text, index) => ({
      id: index + 1,
      text
    }))
  };

  fs.writeFileSync(outputPath, JSON.stringify(payload, null, 2), "utf-8");
  await browser.close();
  console.log(`Saved ${uniqueReviews.length} reviews to ${outputPath}`);
}

const url = process.argv[2];
const outputPath = process.argv[3] || "reviews.json";

if (!url) {
  console.error("Usage: node scrape_reviews.js <url> [output.json]");
  process.exit(1);
}

scrape(url, outputPath).catch((err) => {
  console.error("Scrape failed:", err.message);
  process.exit(1);
});

