import json
import time
import requests
from datetime import datetime

def fetch_reddit_data():
    # Order of priority
    subreddits = ["claudeskills", "ClaudeAI", "claude"]
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    headers = {"User-Agent": user_agent}
    
    all_items = []
    seen_texts = set()
    target_count = 700 # Target slightly more to ensure at least 700 after duplicates/filtering
    
    def add_item(text, sub, created_utc):
        if not text:
            return
        # Filter 1-word
        if len(text.split()) <= 1:
            return
        
        # Deduplicate
        if text in seen_texts:
            return
        
        dt = datetime.fromtimestamp(created_utc).isoformat() if created_utc else datetime.now().isoformat()
        all_items.append({
            "source": "reddit",
            "subreddit": f"r/{sub}",
            "text": text,
            "created_at": dt
        })
        seen_texts.add(text)

    for sub in subreddits:
        print(f"Fetching from r/{sub}...")
        after = None
        pages_to_fetch = 15
        
        for page in range(pages_to_fetch):
            if len(all_items) >= target_count:
                break
                
            url = f"https://www.reddit.com/r/{sub}/new.json?limit=100"
            if after:
                url += f"&after={after}"
            
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 429:
                    print(f"Rate limited (429). Waiting 30s...")
                    time.sleep(30)
                    response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    print(f"Failed to fetch r/{sub} page {page}: {response.status_code}")
                    break
                
                data = response.json()
                children = data.get("data", {}).get("children", [])
                if not children:
                    break
                
                for post in children:
                    pdata = post["data"]
                    title = pdata.get("title", "")
                    body = pdata.get("selftext", "")
                    combined_text = f"{title}\n\n{body}" if body else title
                    add_item(combined_text, sub, pdata.get("created_utc"))
                    
                    # Fetch comments only if we are far from target and post is large
                    if pdata.get("num_comments", 0) > 10 and len(all_items) < target_count * 0.7:
                        comment_url = f"https://www.reddit.com/r/{sub}/comments/{pdata['id']}.json"
                        c_resp = requests.get(comment_url, headers=headers)
                        if c_resp.status_code == 200:
                            c_data = c_resp.json()
                            if isinstance(c_data, list) and len(c_data) > 1:
                                comments = c_data[1].get("data", {}).get("children", [])
                                for comment in comments[:10]: # Only top 10 comments
                                    if comment["kind"] == "t1":
                                        cbody = comment["data"].get("body", "")
                                        if cbody and cbody not in ["[deleted]", "[removed]"]:
                                            add_item(cbody, sub, comment["data"].get("created_utc"))
                        time.sleep(1.5) # Increased throttle
                
                after = data.get("data", {}).get("after")
                if not after:
                    break
                
                time.sleep(2) # Increased sleep between pages
            except Exception as e:
                print(f"Error fetching r/{sub}: {e}")
                break
                
        print(f"Current total items: {len(all_items)}")

    # Final trim and save
    final_items = all_items[:750] # Cap it reasonably
    print(f"Saving {len(final_items)} items to reddit_reviews.json")
    
    with open("reddit_reviews.json", "w", encoding="utf-8") as f:
        json.dump(final_items, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    fetch_reddit_data()
