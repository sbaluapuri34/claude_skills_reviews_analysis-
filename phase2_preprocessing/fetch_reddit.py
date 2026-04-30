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
    target_count = 2100 # Target enough for 700 per sub
    
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

    # target_count is set above
    
    for sub in subreddits:
        print(f"Fetching from r/{sub}...")
        after = None
        pages_to_fetch = 25 # Very deep fetch
        sub_count = 0
        
        for page in range(pages_to_fetch):
            if sub_count >= 700: 
                break
                
            url = f"https://www.reddit.com/r/{sub}/new.json?limit=100"
            if after:
                url += f"&after={after}"
            
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 429:
                    print(f"Rate limited (429) on r/{sub}. Waiting 90s...")
                    time.sleep(90) # Longer wait for deep fetch
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
                    
                    if combined_text and len(combined_text.split()) > 1 and combined_text not in seen_texts:
                        dt = datetime.fromtimestamp(pdata.get("created_utc")).isoformat()
                        all_items.append({
                            "source": "reddit",
                            "subreddit": f"r/{sub}",
                            "text": combined_text,
                            "created_at": dt
                        })
                        seen_texts.add(combined_text)
                        sub_count += 1
                    
                    # Fetch comments sparingly but enough to reach target
                    if pdata.get("num_comments", 0) > 3 and sub_count < 700:
                        comment_url = f"https://www.reddit.com/r/{sub}/comments/{pdata['id']}.json"
                        c_resp = requests.get(comment_url, headers=headers)
                        if c_resp.status_code == 200:
                            c_data = c_resp.json()
                            if isinstance(c_data, list) and len(c_data) > 1:
                                comments = c_data[1].get("data", {}).get("children", [])
                                for comment in comments[:15]: # More comments
                                    if comment["kind"] == "t1":
                                        cbody = comment["data"].get("body", "")
                                        if cbody and cbody not in ["[deleted]", "[removed]"] and cbody not in seen_texts:
                                            all_items.append({
                                                "source": "reddit",
                                                "subreddit": f"r/{sub}",
                                                "text": cbody,
                                                "created_at": datetime.fromtimestamp(comment["data"].get("created_utc")).isoformat()
                                            })
                                            seen_texts.add(cbody)
                                            sub_count += 1
                                            if sub_count >= 700: break
                        time.sleep(2)
                
                after = data.get("data", {}).get("after")
                if not after:
                    break
                
                time.sleep(4)
            except Exception as e:
                print(f"Error fetching r/{sub}: {e}")
                break
        
        print(f"Fetched {sub_count} items from r/{sub}. Total: {len(all_items)}")
                
        print(f"Current total items: {len(all_items)}")

    # Final trim and save
    final_items = all_items[:2100] # Cap it high for multi-source depth
    print(f"Saving {len(final_items)} items to reddit_reviews.json")
    
    with open("reddit_reviews.json", "w", encoding="utf-8") as f:
        json.dump(final_items, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    fetch_reddit_data()
