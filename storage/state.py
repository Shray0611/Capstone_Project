from storage.file_store import load_seen_urls, save_seen_urls, get_rate_limit, increment_rate_limit
from config import MAX_REQUESTS_PER_DOMAIN_PER_DAY

def can_scrape(domain: str) -> bool:
    """Check if domain is allowed to be scraped now."""
    seen = load_seen_urls()
    if domain in seen:
        print(f"Domain {domain} already scraped in this session. Skipping.")
        return False
    
    count = get_rate_limit(domain)
    if count >= MAX_REQUESTS_PER_DOMAIN_PER_DAY:
        print(f"Rate limit reached for {domain} (max {MAX_REQUESTS_PER_DOMAIN_PER_DAY} per day).")
        return False
    
    return True

def mark_scraped(domain: str):
    seen = load_seen_urls()
    seen.add(domain)
    save_seen_urls(seen)
    increment_rate_limit(domain)