const fs = require("fs");
const gplayModule = require("google-play-scraper");
const gplay = gplayModule.default || gplayModule;

async function fetchGooglePlayReviews() {
  const appId = "com.anthropic.claude";
  const targetCount = 100;
  const pageSize = 200;
  const newestSort =
    (gplay.sort && (gplay.sort.NEWEST ?? gplay.sort.newest)) ??
    4; // library fallback for NEWEST

  const raw = await gplay.reviews({
    appId,
    lang: "en",
    country: "us",
    sort: newestSort,
    num: pageSize
  });

  const reviews = (raw.data || [])
    .slice(0, targetCount)
    .map((review) => ({
      text: (review.text || "").trim(),
      score: review.score ?? null,
      date: review.date ? new Date(review.date).toISOString().split("T")[0] : null
    }))
    .filter((r) => r.text.length > 0);

  if (reviews.length < targetCount) {
    throw new Error(`Only fetched ${reviews.length} reviews; expected at least ${targetCount}.`);
  }

  fs.writeFileSync(
    "google_play_reviews.json",
    JSON.stringify(
      {
        appId,
        fetched_at_utc: new Date().toISOString(),
        total_reviews: reviews.length,
        reviews
      },
      null,
      2
    ),
    "utf-8"
  );

  console.log(`Saved ${reviews.length} reviews to google_play_reviews.json`);
}

fetchGooglePlayReviews().catch((err) => {
  console.error("Failed to fetch Google Play reviews:", err.message);
  process.exit(1);
});

