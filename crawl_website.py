import asyncio
from scraper.scrape_engine import crawl_entire_website
from storage.file_store import save_full_crawl

async def main():
    # Option 1: Scrape multiple websites
    print("\n=== MULTI-WEBSITE SCRAPER ===")
    print("Enter domains to crawl (comma-separated, or leave blank for examples):")
    print("Examples: webscraper.io, scrapethissite.com, books.toscrape.com")
    user_input = input("Domains: ").strip()
    
    if not user_input:
        # Use sample websites if no input
        domains = [
            "www.webscraper.io",
            "scrapethissite.com",
            "books.toscrape.com"
        ]
        print(f"Using default sample websites: {', '.join(domains)}")
    else:
        # Parse comma-separated domains
        domains = [d.strip() for d in user_input.split(",") if d.strip()]
    
    for domain in domains:
        try:
            print(f"\n{'='*50}")
            print(f"Starting full crawl of {domain} ...")
            data = await crawl_entire_website(domain)
            save_full_crawl(domain, data)
            print(f"✓ Crawled {data['pages_crawled']} pages from {domain}")
            if data['pages'] and 'text' in data['pages'][0]:
                print(f"  First page sample: {data['pages'][0]['text'][:100]}...")
            if data['pages'] and 'images' in data['pages'][0]:
                print(f"  Images found: {len(data['pages'][0]['images'])}")
        except Exception as e:
            print(f"✗ Failed to crawl {domain}: {e}")
    
    print(f"\n{'='*50}")
    print("All domains processed!")

if __name__ == "__main__":
    asyncio.run(main())