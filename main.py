import asyncio
from scraper.scrape_engine import crawl_entire_website
from storage.file_store import save_full_crawl

async def scrape_website(domain: str):
    """
    Scrape entire website - all pages, text, and images.
    Automatically crawls the entire site and stores everything organized.
    """
    from config import PROTOTYPE_MODE
    
    # Normalize domain input
    domain = domain.strip().lower()
    if domain.startswith(("http://", "https://")):
        from urllib.parse import urlparse
        domain = urlparse(domain).netloc
    
    print("\n" + "="*70)
    print(f"🌐 SCRAPING WEBSITE: {domain}")
    print("="*70)
    
    mode_text = "PROTOTYPE MODE (Limited data for demo)" if PROTOTYPE_MODE else "FULL MODE (Complete crawl)"
    print(f"\n🔧 Mode: {mode_text}")
    
    print(f"\n📌 This will:")
    print(f"   • Crawl pages on the website")
    print(f"   • Download all unique images (no duplicates)")
    print(f"   • Extract all text content")
    print(f"   • Save everything organized in data/ folder\n")
    
    try:
        print(f"⏳ Starting crawl...\n")
        
        # Crawl entire website
        data = await crawl_entire_website(domain)
        
        # Save all data
        save_full_crawl(domain, data)
        
        # Extract detailed statistics
        pages_crawled = data.get('pages_crawled', 0)
        total_images = data.get('total_images_downloaded', 0)
        total_text = data.get('total_text_characters', 0)
        
        # Show per-page breakdown
        print("\n" + "-"*70)
        print("📄 PAGE-BY-PAGE BREAKDOWN:")
        print("-"*70)
        for i, page in enumerate(data['pages'], 1):
            url = page.get('url', 'Unknown')
            text_len = page.get('text_length', 0)
            img_count = page.get('image_count', 0)
            if 'error' not in page:
                print(f"{i}. {url}")
                print(f"   ✓ Text: {text_len:,} characters | Images: {img_count}")
            else:
                print(f"{i}. {url}")
                print(f"   ✗ Error: {page.get('error', 'Unknown error')}")
        
        print("\n" + "="*70)
        print("✅ SCRAPING COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📊 TOTAL RESULTS:")
        print(f"   ✓ Pages crawled: {pages_crawled}")
        print(f"   ✓ Images downloaded: {total_images}")
        print(f"   ✓ Text extracted: {total_text:,} characters")
        print(f"\n📁 Data saved to:")
        print(f"   • JSON data: data/crawls/{domain}_*.json")
        print(f"   • Images: data/images/{domain}/")
        print(f"   • Each page's text & images in the JSON file\n")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to scrape {domain}")
        print(f"   Details: {e}\n")
        import traceback
        traceback.print_exc()
        return False
        
        print("\n" + "="*70)
        print("✅ SCRAPING COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📊 TOTAL RESULTS:")
        print(f"   ✓ Pages crawled: {pages_crawled}")
        print(f"   ✓ Images downloaded: {total_images}")
        print(f"   ✓ Text extracted: {total_text:,} characters")
        print(f"\n📁 Data saved to:")
        print(f"   • JSON data: data/crawls/{domain}_*.json")
        print(f"   • Images: data/images/{domain}/")
        print(f"   • Each page's text & images in the JSON file\n")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to scrape {domain}")
        print(f"   Details: {e}\n")
        import traceback
        traceback.print_exc()
        return False

async def main():
    from config import PROTOTYPE_MODE, MAX_CRAWL_PAGES, MAX_CRAWL_DEPTH, MAX_IMAGES_PER_PAGE
    
    print("\n" + "="*70)
    print("🚀 SIMPLE WEBSITE SCRAPER")
    print("="*70)
    
    # Show current mode
    if PROTOTYPE_MODE:
        print("\n📱 PROTOTYPE MODE (Fast Demo)")
        print(f"   • Max pages: {MAX_CRAWL_PAGES}")
        print(f"   • Crawl depth: {MAX_CRAWL_DEPTH}")
        print(f"   • Images per page: {MAX_IMAGES_PER_PAGE}")
        print(f"   • Estimated time: 2-3 minutes\n")
        print("   💡 TIP: Edit config.py and set PROTOTYPE_MODE = False for full crawl")
    else:
        print("\n🔍 FULL MODE (Complete Crawl)")
        print(f"   • Max pages: {MAX_CRAWL_PAGES}")
        print(f"   • Crawl depth: {MAX_CRAWL_DEPTH}")
        print(f"   • Images per page: {MAX_IMAGES_PER_PAGE}")
        print(f"   • Estimated time: 15-20 minutes\n")
    
    print("Enter a website URL to scrape all content (text, images, data)")
    print("Example inputs:")
    print("  • example.com")
    print("  • www.example.com")
    print("  • https://example.com")
    print("  • books.toscrape.com\n")
    
    website = input("Enter website to scrape: ").strip()
    
    if not website:
        print("❌ No website entered. Exiting.")
        return
    
    success = await scrape_website(website)
    
    if success:
        print("✨ Done! Check the 'data/' folder to see all your scraped content.")
    else:
        print("💡 Tip: Make sure the website is valid and accessible.")

if __name__ == "__main__":
    asyncio.run(main())
