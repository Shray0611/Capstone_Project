import re
import base64
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import aiofiles
import os
import uuid
from config import MIN_IMAGE_WIDTH, MIN_IMAGE_HEIGHT

def extract_clean_text(html: str) -> str:
    """Remove scripts, styles, and extra whitespace."""
    soup = BeautifulSoup(html, "lxml")
    
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()
    
    text = soup.get_text(separator="\n")
    # Clean up lines
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = "\n".join(chunk for chunk in chunks if chunk)
    return text

async def download_images_on_page(page, domain, page_type, globally_downloaded_images=None):
    """Find all <img> tags, filter by size, download and save to disk.
    Uses global tracking to prevent duplicate downloads across entire crawl."""
    import os
    import uuid
    import httpx
    import hashlib
    from config import MAX_IMAGES_PER_PAGE
    
    # Initialize global tracking if not provided
    if globally_downloaded_images is None:
        globally_downloaded_images = set()
    
    # Sanitize page_type for folder name
    safe_page_type = "".join(c if c.isalnum() or c in "._-" else "_" for c in page_type)
    if not safe_page_type or safe_page_type == "":
        safe_page_type = "home"
    
    # Create directory using os.path.join for Windows
    dir_path = os.path.join("data", "images", domain, safe_page_type)
    os.makedirs(dir_path, exist_ok=True)
    
    images = await page.query_selector_all("img")
    saved_paths = []
    
    # Use httpx for downloading images
    async with httpx.AsyncClient(timeout=10) as client:
        for img in images[:MAX_IMAGES_PER_PAGE]:  # Use config limit
            try:
                src = await img.get_attribute("src")
                if not src:
                    continue
                
                # Build absolute URL
                from urllib.parse import urljoin
                img_url = urljoin(page.url, src)
                
                # Skip data URIs and SVGs
                if img_url.startswith('data:') or img_url.endswith('.svg'):
                    continue
                
                # Download using httpx
                try:
                    resp = await client.get(img_url)
                    if resp.status_code == 200:
                        img_bytes = resp.content
                        if len(img_bytes) < 2000:  # skip small icons
                            continue
                        
                        # Calculate hash of image content for global deduplication
                        img_hash = hashlib.md5(img_bytes).hexdigest()
                        
                        # Check if this exact image was already downloaded in this crawl session
                        if img_hash in globally_downloaded_images:
                            # Skip - already downloaded this image across entire crawl
                            continue
                        
                        # Mark as downloaded globally (across entire crawl)
                        globally_downloaded_images.add(img_hash)
                        
                        # Generate safe filename
                        ext = img_url.split('.')[-1].split('?')[0].lower()
                        if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                            ext = 'jpg'
                        filename = f"{domain}_{safe_page_type}_{uuid.uuid4().hex[:8]}.{ext}"
                        file_path = os.path.join(dir_path, filename)
                        
                        # Save image
                        with open(file_path, "wb") as f:
                            f.write(img_bytes)
                        
                        saved_paths.append(file_path)
                        
                except Exception as download_err:
                    # Skip failed downloads silently
                    continue
                    
            except Exception as e:
                # Silently skip failed image extraction
                continue
    
    return saved_paths