const fs = require("fs");

function main() {
  const inputPath = "google_play_reviews.json";
  const outputPath = "google_play_reviews_clean.json";

  const raw = JSON.parse(fs.readFileSync(inputPath, "utf-8"));
  const reviews = Array.isArray(raw.reviews) ? raw.reviews : [];

  const cleaned = reviews
    .map((r) => (r && typeof r.text === "string" ? r.text.trim() : ""))
    .filter((text) => text.length > 0)
    .map((text) => ({
      source: "google_play",
      text
    }));

  fs.writeFileSync(outputPath, JSON.stringify(cleaned, null, 2), "utf-8");
  console.log(`Saved ${cleaned.length} cleaned reviews to ${outputPath}`);
}

main();

