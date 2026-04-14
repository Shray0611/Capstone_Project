from playwright.async_api import async_playwright
import random
import asyncio
from config import USER_AGENTS

async def get_browser_context():
    """Launch a stealthy browser context."""
    p = await async_playwright().start()
    browser = await p.chromium.launch(
        headless=True,   # Set False for debugging
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage"
        ]
    )
    context = await browser.new_context(
        viewport={"width": 1366, "height": 768},
        user_agent=random.choice(USER_AGENTS),
        locale="en-US",
        timezone_id="America/New_York",
        extra_http_headers={
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "sec-ch-ua": '"Chromium";v="120", "Google Chrome";v="120"'
        }
    )
    return p, browser, context

async def human_behavior(page):
    """Simulate scrolling and mouse movement."""
    # Scroll step by step
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
    await asyncio.sleep(random.uniform(0.5, 1.5))
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    await asyncio.sleep(random.uniform(0.3, 1.0))
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await asyncio.sleep(random.uniform(0.8, 2.0))
    
    # Random mouse move
    await page.mouse.move(
        random.randint(100, 1000),
        random.randint(100, 600)
    )