"""
Forum and VR website scraper for Quest 3 comfort-related content.

Scrapes:
- UploadVR
- Road to VR
- Meta Community Forums
- Best Buy reviews
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, quote_plus

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.utils import (
    get_headers, random_delay, is_quest3_related,
    is_comfort_related, clean_text, truncate_text
)
from backend.database import insert_review


class UploadVRScraper:
    """Scraper for UploadVR articles and comments."""
    
    BASE_URL = "https://uploadvr.com"
    
    def search_articles(self, query: str = "quest 3 comfort") -> List[Dict]:
        """Search for articles on UploadVR."""
        url = f"{self.BASE_URL}/?s={quote_plus(query)}"
        
        try:
            response = requests.get(url, headers=get_headers(), timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            # Find article links
            article_elements = soup.select('article')
            
            for article in article_elements[:20]:
                title_el = article.select_one('h2 a, .entry-title a')
                if title_el:
                    articles.append({
                        'url': title_el.get('href', ''),
                        'title': title_el.get_text(strip=True)
                    })
            
            return articles
        
        except Exception as e:
            print(f"Error searching UploadVR: {e}")
            return []
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """Scrape content from an article page."""
        try:
            response = requests.get(url, headers=get_headers(), timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get title
            title_el = soup.select_one('h1.entry-title, h1')
            title = title_el.get_text(strip=True) if title_el else ""
            
            # Get content
            content_el = soup.select_one('.entry-content, article')
            content = ""
            if content_el:
                paragraphs = content_el.find_all('p')
                content = ' '.join(p.get_text(strip=True) for p in paragraphs[:10])
            
            # Get date
            date_el = soup.select_one('time, .entry-date')
            date_str = date_el.get('datetime', '') if date_el else ""
            date_posted = None
            if date_str:
                try:
                    date_posted = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except:
                    pass
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'date_posted': date_posted
            }
        
        except Exception as e:
            print(f"Error scraping article {url}: {e}")
            return None


class RoadToVRScraper:
    """Scraper for Road to VR articles."""
    
    BASE_URL = "https://www.roadtovr.com"
    
    def search_articles(self, query: str = "quest 3 comfort") -> List[Dict]:
        """Search for articles on Road to VR."""
        url = f"{self.BASE_URL}/?s={quote_plus(query)}"
        
        try:
            response = requests.get(url, headers=get_headers(), timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            article_elements = soup.select('article')
            
            for article in article_elements[:20]:
                title_el = article.select_one('h2 a, .entry-title a')
                if title_el:
                    articles.append({
                        'url': title_el.get('href', ''),
                        'title': title_el.get_text(strip=True)
                    })
            
            return articles
        
        except Exception as e:
            print(f"Error searching Road to VR: {e}")
            return []
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """Scrape content from an article page."""
        try:
            response = requests.get(url, headers=get_headers(), timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title_el = soup.select_one('h1.entry-title, h1')
            title = title_el.get_text(strip=True) if title_el else ""
            
            content_el = soup.select_one('.entry-content, article')
            content = ""
            if content_el:
                paragraphs = content_el.find_all('p')
                content = ' '.join(p.get_text(strip=True) for p in paragraphs[:10])
            
            date_el = soup.select_one('time, .entry-date')
            date_str = date_el.get('datetime', '') if date_el else ""
            date_posted = None
            if date_str:
                try:
                    date_posted = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except:
                    pass
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'date_posted': date_posted
            }
        
        except Exception as e:
            print(f"Error scraping article {url}: {e}")
            return None


class BestBuyScraper:
    """Scraper for Best Buy product reviews."""
    
    BASE_URL = "https://www.bestbuy.com"
    
    # Best Buy SKUs for Quest 3 accessories
    PRODUCT_SKUS = [
        "6559936",  # Meta Quest 3 Elite Strap
        "6559937",  # Meta Quest 3 Elite Strap with Battery
        # Add more SKUs as needed
    ]
    
    def get_product_reviews(self, sku: str) -> List[Dict]:
        """Get reviews for a Best Buy product."""
        url = f"{self.BASE_URL}/site/reviews/{sku}"
        
        try:
            headers = get_headers()
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            reviews = []
            
            review_elements = soup.select('.review-item, [data-track="Review"]')
            
            for review_el in review_elements:
                try:
                    title_el = review_el.select_one('.review-title, h4')
                    body_el = review_el.select_one('.review-body, .pre-white-space')
                    author_el = review_el.select_one('.review-author, .reviewer-name')
                    
                    title = title_el.get_text(strip=True) if title_el else ""
                    body = body_el.get_text(strip=True) if body_el else ""
                    author = author_el.get_text(strip=True) if author_el else "Anonymous"
                    
                    reviews.append({
                        'title': title,
                        'content': body,
                        'author': author,
                        'sku': sku
                    })
                
                except:
                    continue
            
            return reviews
        
        except Exception as e:
            print(f"Error scraping Best Buy SKU {sku}: {e}")
            return []


def scrape_uploadvr():
    """Scrape UploadVR for Quest 3 comfort content."""
    print("\nScraping UploadVR...")
    
    scraper = UploadVRScraper()
    articles_saved = 0
    
    search_queries = [
        "quest 3 comfort",
        "quest 3 accessories",
        "quest 3 elite strap",
        "quest 3 bobovr",
        "meta quest 3 review"
    ]
    
    all_articles = []
    seen_urls = set()
    
    for query in search_queries:
        articles = scraper.search_articles(query)
        for article in articles:
            if article['url'] not in seen_urls:
                all_articles.append(article)
                seen_urls.add(article['url'])
        random_delay(2, 4)
    
    for article in tqdm(all_articles, desc="  Processing articles"):
        data = scraper.scrape_article(article['url'])
        if not data:
            continue
        
        full_text = f"{data['title']} {data['content']}"
        
        if not is_quest3_related(full_text):
            continue
        
        if not is_comfort_related(full_text):
            continue
        
        review_id = insert_review(
            source_name="uploadvr",
            external_id=f"uploadvr_{hash(data['url'])}",
            title=clean_text(data['title']),
            content=clean_text(truncate_text(data['content'], 2000)),
            date_posted=data['date_posted'],
            url=data['url']
        )
        
        if review_id:
            articles_saved += 1
        
        random_delay(2, 4)
    
    print(f"  Saved {articles_saved} articles from UploadVR")
    return articles_saved


def scrape_roadtovr():
    """Scrape Road to VR for Quest 3 comfort content."""
    print("\nScraping Road to VR...")
    
    scraper = RoadToVRScraper()
    articles_saved = 0
    
    search_queries = [
        "quest 3 comfort",
        "quest 3 accessories",
        "quest 3 elite strap",
        "meta quest 3"
    ]
    
    all_articles = []
    seen_urls = set()
    
    for query in search_queries:
        articles = scraper.search_articles(query)
        for article in articles:
            if article['url'] not in seen_urls:
                all_articles.append(article)
                seen_urls.add(article['url'])
        random_delay(2, 4)
    
    for article in tqdm(all_articles, desc="  Processing articles"):
        data = scraper.scrape_article(article['url'])
        if not data:
            continue
        
        full_text = f"{data['title']} {data['content']}"
        
        if not is_quest3_related(full_text):
            continue
        
        if not is_comfort_related(full_text):
            continue
        
        review_id = insert_review(
            source_name="roadtovr",
            external_id=f"roadtovr_{hash(data['url'])}",
            title=clean_text(data['title']),
            content=clean_text(truncate_text(data['content'], 2000)),
            date_posted=data['date_posted'],
            url=data['url']
        )
        
        if review_id:
            articles_saved += 1
        
        random_delay(2, 4)
    
    print(f"  Saved {articles_saved} articles from Road to VR")
    return articles_saved


def scrape_bestbuy():
    """Scrape Best Buy reviews for Quest 3 accessories."""
    print("\nScraping Best Buy...")
    
    scraper = BestBuyScraper()
    reviews_saved = 0
    
    for sku in tqdm(scraper.PRODUCT_SKUS, desc="  Processing products"):
        reviews = scraper.get_product_reviews(sku)
        
        for review in reviews:
            full_text = f"{review['title']} {review['content']}"
            
            if not is_comfort_related(full_text):
                continue
            
            review_id = insert_review(
                source_name="bestbuy",
                external_id=f"bestbuy_{sku}_{hash(review['title'])}",
                title=clean_text(review['title']),
                content=clean_text(review['content']),
                author=review['author'],
                url=f"https://www.bestbuy.com/site/reviews/{sku}"
            )
            
            if review_id:
                reviews_saved += 1
        
        random_delay(3, 6)
    
    print(f"  Saved {reviews_saved} reviews from Best Buy")
    return reviews_saved


def scrape_all_forums():
    """Scrape all VR forums and websites."""
    print("\n" + "="*60)
    print("VR Forum and Website Scraper")
    print("="*60)
    
    total = 0
    
    total += scrape_uploadvr()
    total += scrape_roadtovr()
    total += scrape_bestbuy()
    
    print("\n" + "="*60)
    print(f"Forum scraping complete!")
    print(f"Total content saved: {total}")
    print("="*60)
    
    return total


if __name__ == "__main__":
    scrape_all_forums()
