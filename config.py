import random

# Realistic user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
]

# ========== PROTOTYPE/DEMO MODE ==========
# Set to True for fast scraping (limited data for testing)
# Set to False for full crawl
PROTOTYPE_MODE = True

# Scraping behaviour
if PROTOTYPE_MODE:
    # FAST MODE - Prototype/Demo (2-3 minutes)
    MIN_DELAY_SECONDS = 0.5
    MAX_DELAY_SECONDS = 1.0
    DELAY_BETWEEN_PAGES = 0.3
    MAX_CRAWL_PAGES = 15       # Max 15 pages per domain
    MAX_CRAWL_DEPTH = 1        # Only follow 1 level deep
    MAX_IMAGES_PER_PAGE = 5    # Only 5 images per page
else:
    # FULL MODE - Production crawl (15-20 minutes)
    MIN_DELAY_SECONDS = 2
    MAX_DELAY_SECONDS = 5
    DELAY_BETWEEN_PAGES = 1.0
    MAX_CRAWL_PAGES = 100      # Max 100 pages per domain
    MAX_CRAWL_DEPTH = 3        # Follow 3 levels deep
    MAX_IMAGES_PER_PAGE = 20   # 20 images per page

MAX_RETRIES = 3

# Rate limiting (per domain, per day)
MAX_REQUESTS_PER_DOMAIN_PER_DAY = 50

# What pages to scrape (order matters – homepage first)
DEFAULT_PAGES = ["homepage", "about", "blog", "careers", "products"]

# Image filtering
MIN_IMAGE_WIDTH = 100
MIN_IMAGE_HEIGHT = 100
SAME_DOMAIN_ONLY = True     # Don't follow external links  