"""
YouTube comment scraper for Quest 3 comfort-related videos.

Uses the YouTube Data API v3.
Requires a YouTube API key (get one from Google Cloud Console).
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from tqdm import tqdm

from scraper.utils import (
    random_delay, is_comfort_related, 
    clean_text, truncate_text
)
from backend.database import insert_review

# Load environment variables
load_dotenv()

# Try to import Google API client
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    print("Warning: google-api-python-client not installed. Run: pip install google-api-python-client")

# YouTube API key from environment
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# Search queries for finding Quest 3 comfort videos
SEARCH_QUERIES = [
    "quest 3 comfort",
    "quest 3 best strap",
    "quest 3 elite strap review",
    "quest 3 bobovr m3 pro",
    "quest 3 kiwi strap",
    "quest 3 head strap comparison",
    "quest 3 accessories",
    "quest 3 comfort mods",
    "meta quest 3 comfort",
    "quest 3 face cover review",
    "quest 3 battery strap"
]

# Specific video IDs known to have Quest 3 comfort content
# These are examples - you can add more
KNOWN_VIDEO_IDS = [
    # Add video IDs here if you know specific videos
    # "dQw4w9WgXcQ",  # Example format
]


class YouTubeScraper:
    """YouTube scraper using the YouTube Data API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or YOUTUBE_API_KEY
        self.youtube = None
        
        if self.api_key and YOUTUBE_API_AVAILABLE:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
    
    def search_videos(self, query: str, max_results: int = 25) -> List[Dict]:
        """Search for videos matching a query."""
        if not self.youtube:
            return []
        
        try:
            request = self.youtube.search().list(
                part='snippet',
                q=query,
                type='video',
                maxResults=max_results,
                order='relevance',
                publishedAfter='2023-01-01T00:00:00Z'  # Quest 3 launched in Oct 2023
            )
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                videos.append({
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'channel': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt']
                })
            
            return videos
        
        except HttpError as e:
            print(f"YouTube API error: {e}")
            return []
    
    def get_video_comments(self, video_id: str, max_results: int = 100) -> List[Dict]:
        """Get comments for a specific video."""
        if not self.youtube:
            return []
        
        comments = []
        next_page_token = None
        
        try:
            while len(comments) < max_results:
                request = self.youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=min(100, max_results - len(comments)),
                    pageToken=next_page_token,
                    textFormat='plainText',
                    order='relevance'
                )
                response = request.execute()
                
                for item in response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        'comment_id': item['id'],
                        'text': comment['textDisplay'],
                        'author': comment['authorDisplayName'],
                        'published_at': comment['publishedAt'],
                        'like_count': comment['likeCount'],
                        'video_id': video_id
                    })
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            
            return comments
        
        except HttpError as e:
            if 'commentsDisabled' in str(e):
                print(f"  Comments disabled for video {video_id}")
            else:
                print(f"  Error getting comments for {video_id}: {e}")
            return []
    
    def get_video_details(self, video_id: str) -> Optional[Dict]:
        """Get details for a specific video."""
        if not self.youtube:
            return None
        
        try:
            request = self.youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            )
            response = request.execute()
            
            if response.get('items'):
                item = response['items'][0]
                return {
                    'video_id': video_id,
                    'title': item['snippet']['title'],
                    'channel': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'view_count': int(item['statistics'].get('viewCount', 0)),
                    'like_count': int(item['statistics'].get('likeCount', 0)),
                    'comment_count': int(item['statistics'].get('commentCount', 0))
                }
            
            return None
        
        except HttpError as e:
            print(f"Error getting video details: {e}")
            return None


def parse_youtube_date(date_str: str) -> Optional[datetime]:
    """Parse YouTube date format."""
    try:
        # Format: 2023-12-15T10:30:00Z
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    except:
        return None


def scrape_youtube_comments():
    """Main function to scrape YouTube comments."""
    print("\n" + "="*60)
    print("YouTube Comment Scraper for Quest 3 Comfort Content")
    print("="*60)
    
    if not YOUTUBE_API_KEY:
        print("\nNo YouTube API key found!")
        print("Set YOUTUBE_API_KEY in your .env file to enable YouTube scraping.")
        print("Get an API key from: https://console.cloud.google.com/")
        return 0
    
    if not YOUTUBE_API_AVAILABLE:
        print("\nGoogle API client not available.")
        print("Run: pip install google-api-python-client")
        return 0
    
    scraper = YouTubeScraper()
    total_comments = 0
    processed_videos = set()
    
    # Search for videos
    print("\nSearching for Quest 3 comfort videos...")
    all_videos = []
    
    for query in tqdm(SEARCH_QUERIES, desc="Searching"):
        videos = scraper.search_videos(query, max_results=10)
        for video in videos:
            video_id = video['video_id']
            if video_id not in processed_videos:
                all_videos.append(video)
                processed_videos.add(video_id)
        random_delay(0.5, 1)
    
    # Add known video IDs
    for video_id in KNOWN_VIDEO_IDS:
        if video_id not in processed_videos:
            details = scraper.get_video_details(video_id)
            if details:
                all_videos.append(details)
                processed_videos.add(video_id)
    
    print(f"\nFound {len(all_videos)} unique videos")
    
    # Process each video
    for video in tqdm(all_videos, desc="Processing videos"):
        video_id = video['video_id']
        video_title = video.get('title', '')
        
        # Get comments
        comments = scraper.get_video_comments(video_id, max_results=100)
        video_comments_saved = 0
        
        for comment in comments:
            # Check if comment is comfort-related
            if not is_comfort_related(comment['text']):
                continue
            
            # Parse date
            date_posted = parse_youtube_date(comment['published_at'])
            
            # Insert into database
            review_id = insert_review(
                source_name="youtube",
                external_id=f"yt_{comment['comment_id']}",
                title=f"Comment on: {truncate_text(video_title, 80)}",
                content=clean_text(comment['text']),
                author=comment['author'],
                date_posted=date_posted,
                upvotes=comment['like_count'],
                url=f"https://www.youtube.com/watch?v={video_id}"
            )
            
            if review_id:
                video_comments_saved += 1
                total_comments += 1
        
        if video_comments_saved > 0:
            print(f"  {video_title[:50]}... - {video_comments_saved} comments")
        
        random_delay(0.5, 1)
    
    print("\n" + "="*60)
    print(f"YouTube scraping complete!")
    print(f"Total comments saved: {total_comments}")
    print("="*60)
    
    return total_comments


if __name__ == "__main__":
    scrape_youtube_comments()
