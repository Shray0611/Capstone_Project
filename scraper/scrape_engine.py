import asyncio
import random
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from scraper.browser import get_browser_context, human_behavior
from scraper.extractors import extract_clean_text, download_images_on_page
from config import DEFAULT_PAGES, MIN_DELAY_SECONDS, MAX_DELAY_SECONDS, MAX_RETRIES
from collections import deque
import time

def normalize_url(raw_url):
    """Add https:// if missing, extract domain."""
    if not raw_url.startswith(("http://", "https://")):
        raw_url = "https://" + raw_url
    return raw_url

def clean_url_for_comparison(url):
    """
    Normalize URL for deduplication.
    Removes query params, fragments, and trailing slashes to prevent duplicates.
    """
    parsed = urlparse(url)
    # Keep scheme and netloc and path, remove params, query, and fragment
    cleaned = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')
    return cleaned.lower()

async def find_page_url(page, base_domain, page_type):
    """
    Try to locate the actual URL for a given page type.
    e.g. '/blog' or '/careers' or '/about-us'.
    """
    mappings = {
        "homepage": "/",
        "about": ["/about", "/about-us", "/company", "/our-story"],
        "blog": ["/blog", "/news", "/insights", "/articles"],
        "careers": ["/careers", "/jobs", "/join-us", "/work-with-us"],
        "products": ["/products", "/solutions", "/services", "/what-we-do"]
    }
    
    if page_type == "homepage":
        return f"https://{base_domain}"
    
    for path in mappings.get(page_type, []):
        test_url = f"https://{base_domain}{path}"
        return test_url
    return None
  
async def crawl_entire_website(start_domain: str, max_pages=None, max_depth=None):
    """
    Crawl every page on the domain, extract text & images.
    Prevents duplicate page crawling and image downloads across entire crawl.
    Uses limits from config.py (PROTOTYPE_MODE controls limits).
    """
    from config import MAX_CRAWL_PAGES, MAX_CRAWL_DEPTH, DELAY_BETWEEN_PAGES, PROTOTYPE_MODE
    
    if max_pages is None:
        max_pages = MAX_CRAWL_PAGES
    if max_depth is None:
        max_depth = MAX_CRAWL_DEPTH
    
    # Show mode being used
    mode_label = "📱 PROTOTYPE MODE (fast)" if PROTOTYPE_MODE else "🔍 FULL MODE (complete)"
    print(f"\n{mode_label}")
    print(f"   Limit: {max_pages} pages, depth: {max_depth}")
    
    # Normalize domain
    start_domain = start_domain.lower().strip()
    if start_domain.startswith(("http://", "https://")):
        parsed = urlparse(start_domain)
        start_domain = parsed.netloc
    base_url = f"https://{start_domain}"
    
    # BFS state - stores BOTH original URL and cleaned URL for deduplication
    to_visit = deque([(base_url, 0)])
    visited_urls_cleaned = set([clean_url_for_comparison(base_url)])
    visited_urls_original = set([base_url])
    all_pages = []
    
    # GLOBAL tracking for images across entire crawl (prevents duplicates)
    globally_downloaded_images = set()  # Track image hashes across all pages
    
    p, browser, context = await get_browser_context()
    page = await context.new_page()
    
    try:
        while to_visit and len(all_pages) < max_pages:
            url, depth = to_visit.popleft()
            print(f"Crawling [{depth}] {url}")
            
            # Fetch page
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await human_behavior(page)
                
                html = await page.content()
                text = extract_clean_text(html)
                # Pass the global image tracking set to prevent global duplicates
                folder_name = clean_url_for_comparison(url).replace("https://", "").replace("/", "_") or "home"
                images = await download_images_on_page(page, start_domain, folder_name, globally_downloaded_images)
                
                # Store page data
                all_pages.append({
                    "url": url,
                    "depth": depth,
                    "text": text,
                    "images": images,
                    "text_length": len(text),
                    "image_count": len(images)
                })
                
                print(f"  ✓ Extracted {len(text):,} characters of text, {len(images)} unique images")
                
                # Extract internal links for crawling if depth < max_depth
                if depth < max_depth:
                    soup = BeautifulSoup(html, "lxml")
                    for link in soup.find_all("a", href=True):
                        href = link.get("href")
                        full_url = urljoin(url, href)
                        parsed_full = urlparse(full_url)
                        
                        # Only same domain, skip file downloads
                        if parsed_full.netloc == start_domain and not full_url.endswith(('.pdf', '.jpg', '.png', '.zip', '.doc', '.docx')):
                            # Clean URL for deduplication
                            cleaned_new_url = clean_url_for_comparison(full_url)
                            
                            # Only add if we haven't visited this cleaned URL before
                            if cleaned_new_url not in visited_urls_cleaned:
                                visited_urls_cleaned.add(cleaned_new_url)
                                visited_urls_original.add(full_url)
                                to_visit.append((full_url, depth + 1))
                
                # Polite delay
                await asyncio.sleep(DELAY_BETWEEN_PAGES)
                
            except Exception as e:
                print(f"  ✗ Failed to crawl {url}: {e}")
                all_pages.append({
                    "url": url,
                    "depth": depth,
                    "error": str(e),
                    "text": "",
                    "images": [],
                    "text_length": 0,
                    "image_count": 0
                })
        
    finally:
        await browser.close()
        await p.stop()
    
    # Calculate totals
    total_text = sum(page.get('text_length', 0) for page in all_pages)
    total_images = sum(page.get('image_count', 0) for page in all_pages)
    
    return {
        "domain": start_domain,
        "pages_crawled": len(all_pages),
        "total_text_characters": total_text,
        "total_images_downloaded": total_images,
        "pages": all_pages
    }

async def scrape_company(domain: str, pages_to_scrape=None):
    """
    Main scraping function.
    Returns dict with text and image paths per page.
    """
    if pages_to_scrape is None:
        pages_to_scrape = DEFAULT_PAGES
    
    domain = domain.lower().strip()
    base_url = f"https://{domain}"
    
    p, browser, context = await get_browser_context()
    page = await context.new_page()
    
    results = {}
    
    try:
        # Always start from homepage to set cookies/session
        await page.goto(base_url, wait_until="networkidle", timeout=30000)
        await human_behavior(page)
        
        # Scrape homepage separately (already on it)
        homepage_html = await page.content()
        homepage_text = extract_clean_text(homepage_html)
        homepage_images = await download_images_on_page(page, domain, "homepage")
        results["homepage"] = {
            "text": homepage_text,
            "images": homepage_images,
            "url": base_url
        }
        
        # Then other pages
        for page_type in pages_to_scrape:
            if page_type == "homepage":
                continue
            target_url = await find_page_url(page, domain, page_type)
            if not target_url:
                continue
            
            try:
                await page.goto(target_url, wait_until="networkidle", timeout=20000)
                await human_behavior(page)
                
                html = await page.content()
                text = extract_clean_text(html)
                images = await download_images_on_page(page, domain, page_type)
                
                results[page_type] = {
                    "text": text,
                    "images": images,
                    "url": target_url
                }
                
                # Polite delay between pages
                await asyncio.sleep(random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS))
                
            except Exception as e:
                print(f"Failed to scrape {page_type} for {domain}: {e}")
                results[page_type] = {"error": str(e), "text": "", "images": []}
    
    except Exception as e:
        print(f"Scraping failed for {domain}: {e}")
        raise
    finally:
        await browser.close()
        await p.stop()
    
    return results