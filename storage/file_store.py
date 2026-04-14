import json
import os
from datetime import datetime

def save_scraped_data(domain: str, scraped_data: dict):
    """Save JSON output to data/scraped/{domain}_{timestamp}.json"""
    os.makedirs("data/scraped", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/scraped/{domain}_{timestamp}.json"
    
    # Convert any non-serializable items (like paths)
    serializable = {
        "domain": domain,
        "scraped_at": timestamp,
        "pages": scraped_data
    }
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)
    
    print(f"Saved scraped data to {filename}")
    return filename

def load_seen_urls():
    """Load set of already scraped domains from state file."""
    path = "data/state/seen_urls.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return set(json.load(f))
    return set()

def save_seen_urls(seen_set):
    os.makedirs("data/state", exist_ok=True)
    with open("data/state/seen_urls.json", "w") as f:
        json.dump(list(seen_set), f)

def get_rate_limit(domain):
    """Load request counts per domain."""
    path = "data/state/rate_limits.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            return data.get(domain, 0)
    return 0

def increment_rate_limit(domain):
    os.makedirs("data/state", exist_ok=True)
    path = "data/state/rate_limits.json"
    data = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
    data[domain] = data.get(domain, 0) + 1
    with open(path, "w") as f:
        json.dump(data, f)
        

  
def save_full_crawl(domain: str, crawl_data: dict):
    """Save the entire crawled website to a single JSON file in data/crawls/."""
    os.makedirs("data/crawls", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Sanitize domain for filename (replace slashes)
    safe_domain = domain.replace("/", "_").replace("\\", "_")
    filename = f"data/crawls/{safe_domain}_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(crawl_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Full crawl saved to {filename}")
    return filename