"""
Amazon review scraper for Quest 3 accessories.

NOTE: Web scraping Amazon may violate their Terms of Service.
This scraper is provided for educational purposes only.
For production use, consider:
1. Amazon Product Advertising API (requires affiliate account)
2. Manual data collection
3. Third-party data providers

Use responsibly with appropriate delays and rate limiting.
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, quote_plus

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from playwright.sync_api import sync_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not installed. Run: pip install playwright && playwright install chromium")

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from scraper.utils import (
    get_headers, random_delay, is_comfort_related, 
    clean_text, truncate_text
)
from backend.database import insert_review

# Amazon product ASINs for Quest 3 accessories
# These are example ASINs - you may need to update them
QUEST3_ACCESSORY_ASINS = [
    # Head Straps
    "B0CG6YBP73",  # BoboVR M3 Pro
    "B0CGBT8LFD",  # Kiwi Design Elite Strap
    "B0CFWC1KBS",  # AMVR Head Strap
    "B0CHQTZPTT",  # DESTEK Head Strap
    "B0CLXMQNC2",  # Meta Quest 3 Elite Strap
    
    # Face Covers
    "B0CGC6K72J",  # Kiwi Face Interface
    "B0CGZRK9CH",  # AMVR Face Cover
    "B0CHQV2R5F",  # VR Cover
    
    # Battery Packs
    "B0CG6XPBHT",  # BoboVR M3 Battery
    "B0CLXNFVGY",  # Meta Elite Battery Strap
    
    # Lens Protectors
    "B0CGFHZ38Q",  # ZenNiZe Lens Protector
]

# Search terms for finding Quest 3 accessories
SEARCH_TERMS = [
    "quest 3 head strap",
    "quest 3 elite strap",
    "quest 3 face cover",
    "quest 3 battery strap",
    "quest 3 comfort accessories",
    "quest 3 lens protector",
    "bobovr m3 pro",
    "kiwi quest 3",
]

BASE_URL = "https://www.amazon.com"


def get_review_page_url(asin: str, page: int = 1) -> str:
    """Generate URL for product review page."""
    return f"{BASE_URL}/product-reviews/{asin}?pageNumber={page}&filterByStar=all_stars"


def get_search_url(query: str) -> str:
    """Generate Amazon search URL."""
    return f"{BASE_URL}/s?k={quote_plus(query)}"


class AmazonScraper:
    """Amazon scraper using Playwright for JavaScript rendering."""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    def start(self):
        """Start the browser."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright is not available")
        
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        self.page = self.browser.new_page()
        self.page.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9",
        })
    
    def stop(self):
        """Stop the browser."""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
    
    def get_page_content(self, url: str) -> Optional[str]:
        """Navigate to URL and get page content."""
        try:
            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            random_delay(2, 4)
            return self.page.content()
        except Exception as e:
            print(f"Error loading {url}: {e}")
            return None
    
    def extract_reviews_from_page(self, html: str, product_name: str = "") -> List[Dict]:
        """Extract reviews from Amazon review page HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        reviews = []
        
        # Find review elements
        review_elements = soup.select('[data-hook="review"]')
        
        for review_el in review_elements:
            try:
                # Extract review ID
                review_id = review_el.get('id', '')
                
                # Extract title
                title_el = review_el.select_one('[data-hook="review-title"]')
                title = title_el.get_text(strip=True) if title_el else ""
                
                # Extract body
                body_el = review_el.select_one('[data-hook="review-body"]')
                body = body_el.get_text(strip=True) if body_el else ""
                
                # Extract author
                author_el = review_el.select_one('.a-profile-name')
                author = author_el.get_text(strip=True) if author_el else "Anonymous"
                
                # Extract date
                date_el = review_el.select_one('[data-hook="review-date"]')
                date_text = date_el.get_text(strip=True) if date_el else ""
                date_posted = self._parse_date(date_text)
                
                # Extract rating
                rating_el = review_el.select_one('[data-hook="review-star-rating"]')
                rating = 0
                if rating_el:
                    rating_text = rating_el.get_text(strip=True)
                    match = re.search(r'(\d+\.?\d*)', rating_text)
                    if match:
                        rating = float(match.group(1))
                
                # Extract helpful votes
                helpful_el = review_el.select_one('[data-hook="helpful-vote-statement"]')
                helpful_votes = 0
                if helpful_el:
                    helpful_text = helpful_el.get_text(strip=True)
                    match = re.search(r'(\d+)', helpful_text)
                    if match:
                        helpful_votes = int(match.group(1))
                
                reviews.append({
                    'external_id': review_id,
                    'title': clean_text(title),
                    'content': clean_text(body),
                    'author': author,
                    'date_posted': date_posted,
                    'rating': rating,
                    'helpful_votes': helpful_votes,
                    'product_name': product_name
                })
            
            except Exception as e:
                print(f"Error extracting review: {e}")
                continue
        
        return reviews
    
    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse Amazon date format."""
        # Format: "Reviewed in the United States on December 15, 2023"
        match = re.search(r'on (\w+ \d+, \d+)', date_text)
        if match:
            try:
                return datetime.strptime(match.group(1), "%B %d, %Y")
            except:
                pass
        return None
    
    def get_product_info(self, html: str) -> Dict:
        """Extract product information from product page."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Get product title
        title_el = soup.select_one('#productTitle')
        title = title_el.get_text(strip=True) if title_el else ""
        
        # Get average rating
        rating_el = soup.select_one('[data-hook="rating-out-of-text"]')
        rating = 0
        if rating_el:
            match = re.search(r'(\d+\.?\d*)', rating_el.get_text())
            if match:
                rating = float(match.group(1))
        
        # Get review count
        count_el = soup.select_one('[data-hook="total-review-count"]')
        review_count = 0
        if count_el:
            match = re.search(r'([\d,]+)', count_el.get_text())
            if match:
                review_count = int(match.group(1).replace(',', ''))
        
        return {
            'title': title,
            'rating': rating,
            'review_count': review_count
        }
    
    def scrape_product_reviews(self, asin: str, max_pages: int = 5) -> int:
        """Scrape reviews for a single product."""
        reviews_saved = 0
        
        # First get product info
        product_url = f"{BASE_URL}/dp/{asin}"
        html = self.get_page_content(product_url)
        if not html:
            return 0
        
        product_info = self.get_product_info(html)
        product_name = product_info.get('title', asin)
        print(f"  Product: {truncate_text(product_name, 60)}")
        
        # Scrape review pages
        for page_num in range(1, max_pages + 1):
            url = get_review_page_url(asin, page_num)
            html = self.get_page_content(url)
            
            if not html:
                break
            
            reviews = self.extract_reviews_from_page(html, product_name)
            
            if not reviews:
                break
            
            for review in reviews:
                # Check if review is comfort-related
                full_text = f"{review['title']} {review['content']}"
                if not is_comfort_related(full_text):
                    continue
                
                # Insert into database
                review_id = insert_review(
                    source_name="amazon",
                    external_id=f"amazon_{asin}_{review['external_id']}",
                    title=f"{review['title']} - {truncate_text(product_name, 50)}",
                    content=review['content'],
                    author=review['author'],
                    date_posted=review['date_posted'],
                    upvotes=review['helpful_votes'],
                    url=f"{BASE_URL}/dp/{asin}"
                )
                
                if review_id:
                    reviews_saved += 1
            
            random_delay(3, 6)
        
        return reviews_saved


def scrape_amazon_reviews_simple():
    """
    Simplified scraper using requests + BeautifulSoup.
    Less reliable but doesn't require Playwright.
    """
    print("\n" + "="*60)
    print("Amazon Review Scraper (Simple Mode)")
    print("="*60)
    print("\nNote: This scraper may be blocked by Amazon.")
    print("For reliable scraping, use Playwright mode.\n")
    
    total_reviews = 0
    
    for asin in tqdm(QUEST3_ACCESSORY_ASINS, desc="Scraping products"):
        url = get_review_page_url(asin)
        headers = get_headers()
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code != 200:
                print(f"  Failed to fetch {asin}: HTTP {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            review_elements = soup.select('[data-hook="review"]')
            
            for review_el in review_elements:
                try:
                    review_id = review_el.get('id', '')
                    title_el = review_el.select_one('[data-hook="review-title"]')
                    body_el = review_el.select_one('[data-hook="review-body"]')
                    
                    title = title_el.get_text(strip=True) if title_el else ""
                    body = body_el.get_text(strip=True) if body_el else ""
                    
                    full_text = f"{title} {body}"
                    if not is_comfort_related(full_text):
                        continue
                    
                    db_id = insert_review(
                        source_name="amazon",
                        external_id=f"amazon_{asin}_{review_id}",
                        title=clean_text(title),
                        content=clean_text(body),
                        url=f"{BASE_URL}/dp/{asin}"
                    )
                    
                    if db_id:
                        total_reviews += 1
                
                except Exception as e:
                    continue
            
            random_delay(5, 10)
        
        except Exception as e:
            print(f"  Error scraping {asin}: {e}")
    
    print(f"\nTotal reviews saved: {total_reviews}")
    return total_reviews


def scrape_amazon_reviews():
    """Main function to scrape Amazon reviews."""
    print("\n" + "="*60)
    print("Amazon Review Scraper for Quest 3 Accessories")
    print("="*60)
    
    if not PLAYWRIGHT_AVAILABLE:
        print("\nPlaywright not available. Using simple mode.")
        return scrape_amazon_reviews_simple()
    
    scraper = AmazonScraper()
    total_reviews = 0
    
    try:
        scraper.start()
        
        for asin in tqdm(QUEST3_ACCESSORY_ASINS, desc="Scraping products"):
            try:
                reviews = scraper.scrape_product_reviews(asin, max_pages=3)
                total_reviews += reviews
                print(f"    Saved {reviews} comfort-related reviews")
            except Exception as e:
                print(f"  Error scraping {asin}: {e}")
            
            random_delay(5, 10)
    
    finally:
        scraper.stop()
    
    print("\n" + "="*60)
    print(f"Amazon scraping complete!")
    print(f"Total reviews saved: {total_reviews}")
    print("="*60)
    
    return total_reviews


if __name__ == "__main__":
    scrape_amazon_reviews()
