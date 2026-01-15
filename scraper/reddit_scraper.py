"""Reddit scraper for Quest 3 comfort-related posts and comments."""

import requests
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.utils import (
    get_headers, random_delay, is_quest3_related, 
    is_comfort_related, clean_text, truncate_text
)
from backend.database import insert_review, get_connection

# Subreddits to scrape
SUBREDDITS = [
    "OculusQuest",
    "Quest3", 
    "metaquest",
    "VirtualReality",
    "oculus"
]

# Search queries for finding relevant posts
SEARCH_QUERIES = [
    "quest 3 comfort",
    "quest 3 strap",
    "quest 3 head strap",
    "quest 3 elite strap",
    "quest 3 bobo",
    "quest 3 bobovr",
    "quest 3 kiwi",
    "quest 3 face cover",
    "quest 3 face interface",
    "quest 3 weight",
    "quest 3 uncomfortable",
    "quest 3 comfortable",
    "quest 3 accessories",
    "quest 3 accessory",
    "quest 3 battery strap",
    "meta quest 3 comfort",
    "best quest 3 strap",
    "quest 3 prescription lens"
]


def fetch_reddit_json(url: str) -> Optional[Dict]:
    """Fetch JSON data from Reddit."""
    headers = get_headers()
    headers["Accept"] = "application/json"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def get_subreddit_posts(subreddit: str, sort: str = "hot", limit: int = 100) -> List[Dict]:
    """Get posts from a subreddit using JSON endpoint."""
    posts = []
    after = None
    fetched = 0
    
    while fetched < limit:
        batch_size = min(100, limit - fetched)
        url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={batch_size}"
        if after:
            url += f"&after={after}"
        
        data = fetch_reddit_json(url)
        if not data or "data" not in data:
            break
        
        children = data["data"].get("children", [])
        if not children:
            break
        
        for child in children:
            post_data = child.get("data", {})
            posts.append(post_data)
        
        after = data["data"].get("after")
        if not after:
            break
        
        fetched += len(children)
        random_delay(1, 2)
    
    return posts


def search_subreddit(subreddit: str, query: str, limit: int = 50) -> List[Dict]:
    """Search a subreddit for posts matching a query."""
    posts = []
    after = None
    fetched = 0
    
    while fetched < limit:
        batch_size = min(100, limit - fetched)
        url = f"https://www.reddit.com/r/{subreddit}/search.json?q={query}&restrict_sr=on&limit={batch_size}&sort=relevance"
        if after:
            url += f"&after={after}"
        
        data = fetch_reddit_json(url)
        if not data or "data" not in data:
            break
        
        children = data["data"].get("children", [])
        if not children:
            break
        
        for child in children:
            post_data = child.get("data", {})
            posts.append(post_data)
        
        after = data["data"].get("after")
        if not after:
            break
        
        fetched += len(children)
        random_delay(1, 2)
    
    return posts


def get_post_comments(permalink: str, limit: int = 200) -> List[Dict]:
    """Get comments for a specific post."""
    url = f"https://www.reddit.com{permalink}.json?limit={limit}"
    
    data = fetch_reddit_json(url)
    if not data or len(data) < 2:
        return []
    
    comments = []
    
    def extract_comments(comment_data: Dict, depth: int = 0):
        """Recursively extract comments."""
        if depth > 5:  # Limit depth
            return
        
        if comment_data.get("kind") != "t1":
            return
        
        comment = comment_data.get("data", {})
        if comment.get("body"):
            comments.append(comment)
        
        # Get replies
        replies = comment.get("replies")
        if replies and isinstance(replies, dict):
            children = replies.get("data", {}).get("children", [])
            for child in children:
                extract_comments(child, depth + 1)
    
    # Process top-level comments
    for item in data[1].get("data", {}).get("children", []):
        extract_comments(item)
    
    return comments


def process_post(post: Dict, source_name: str = "reddit") -> Optional[int]:
    """Process a Reddit post and store it in the database."""
    title = post.get("title", "")
    selftext = post.get("selftext", "")
    
    # Combine title and body for relevance checking
    full_text = f"{title} {selftext}"
    
    # Check if post is Quest 3 and comfort related
    if not is_quest3_related(full_text):
        return None
    
    if not is_comfort_related(full_text):
        return None
    
    # Extract post data
    external_id = post.get("id", "")
    author = post.get("author", "[deleted]")
    created_utc = post.get("created_utc", 0)
    date_posted = datetime.fromtimestamp(created_utc) if created_utc else None
    upvotes = post.get("ups", 0)
    permalink = post.get("permalink", "")
    url = f"https://reddit.com{permalink}" if permalink else ""
    
    # Clean and prepare content
    content = clean_text(selftext) if selftext else ""
    title = clean_text(title)
    
    # Insert into database
    review_id = insert_review(
        source_name=source_name,
        external_id=f"post_{external_id}",
        title=title,
        content=content,
        author=author,
        date_posted=date_posted,
        upvotes=upvotes,
        url=url
    )
    
    return review_id


def process_comment(comment: Dict, post_title: str, source_name: str = "reddit") -> Optional[int]:
    """Process a Reddit comment and store it in the database."""
    body = comment.get("body", "")
    
    if not body or body in ["[deleted]", "[removed]"]:
        return None
    
    # Check if comment is comfort related
    if not is_comfort_related(body):
        return None
    
    # Extract comment data
    external_id = comment.get("id", "")
    author = comment.get("author", "[deleted]")
    created_utc = comment.get("created_utc", 0)
    date_posted = datetime.fromtimestamp(created_utc) if created_utc else None
    upvotes = comment.get("ups", 0)
    permalink = comment.get("permalink", "")
    url = f"https://reddit.com{permalink}" if permalink else ""
    
    # Clean content
    content = clean_text(body)
    
    # Use post title as the title for context
    title = f"Re: {truncate_text(post_title, 100)}"
    
    # Insert into database
    review_id = insert_review(
        source_name=source_name,
        external_id=f"comment_{external_id}",
        title=title,
        content=content,
        author=author,
        date_posted=date_posted,
        upvotes=upvotes,
        url=url
    )
    
    return review_id


def scrape_subreddit(subreddit: str, posts_limit: int = 200, comments_per_post: int = 100):
    """Scrape a single subreddit for Quest 3 comfort content."""
    print(f"\n{'='*50}")
    print(f"Scraping r/{subreddit}")
    print(f"{'='*50}")
    
    all_posts = []
    seen_ids = set()
    
    # Get posts from different sort methods
    for sort in ["hot", "new", "top"]:
        print(f"  Fetching {sort} posts...")
        posts = get_subreddit_posts(subreddit, sort=sort, limit=posts_limit // 3)
        for post in posts:
            post_id = post.get("id")
            if post_id and post_id not in seen_ids:
                all_posts.append(post)
                seen_ids.add(post_id)
        random_delay(2, 4)
    
    # Search for specific queries
    print(f"  Searching for comfort-related posts...")
    for query in SEARCH_QUERIES[:5]:  # Limit queries per subreddit
        posts = search_subreddit(subreddit, query, limit=30)
        for post in posts:
            post_id = post.get("id")
            if post_id and post_id not in seen_ids:
                all_posts.append(post)
                seen_ids.add(post_id)
        random_delay(2, 4)
    
    print(f"  Found {len(all_posts)} unique posts")
    
    # Process posts and comments
    posts_saved = 0
    comments_saved = 0
    
    for post in tqdm(all_posts, desc=f"  Processing r/{subreddit}"):
        # Process the post itself
        review_id = process_post(post)
        if review_id:
            posts_saved += 1
        
        # Get and process comments if post is relevant
        title = post.get("title", "")
        selftext = post.get("selftext", "")
        full_text = f"{title} {selftext}"
        
        if is_quest3_related(full_text):
            permalink = post.get("permalink")
            if permalink:
                comments = get_post_comments(permalink, limit=comments_per_post)
                for comment in comments:
                    comment_id = process_comment(comment, title)
                    if comment_id:
                        comments_saved += 1
                random_delay(1, 2)
    
    print(f"  Saved {posts_saved} posts and {comments_saved} comments")
    return posts_saved, comments_saved


def scrape_all_subreddits():
    """Scrape all configured subreddits."""
    print("\n" + "="*60)
    print("Reddit Scraper for Quest 3 Comfort Content")
    print("="*60)
    
    total_posts = 0
    total_comments = 0
    
    for subreddit in SUBREDDITS:
        try:
            posts, comments = scrape_subreddit(subreddit)
            total_posts += posts
            total_comments += comments
        except Exception as e:
            print(f"Error scraping r/{subreddit}: {e}")
        
        # Longer delay between subreddits
        random_delay(5, 10)
    
    print("\n" + "="*60)
    print(f"Reddit scraping complete!")
    print(f"Total posts saved: {total_posts}")
    print(f"Total comments saved: {total_comments}")
    print("="*60)
    
    return total_posts, total_comments


if __name__ == "__main__":
    scrape_all_subreddits()
