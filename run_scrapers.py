#!/usr/bin/env python3
"""
Main script to run all scrapers and analyzers for Quest 3 Comfort Analyzer.

Usage:
    python run_scrapers.py           # Run everything
    python run_scrapers.py --scrape  # Only run scrapers
    python run_scrapers.py --analyze # Only run analyzers
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.database import init_database


def run_scrapers():
    """Run all web scrapers."""
    print("\n" + "="*70)
    print("RUNNING WEB SCRAPERS")
    print("="*70)
    
    # Reddit scraper
    print("\n[1/4] Reddit Scraper")
    try:
        from scraper.reddit_scraper import scrape_all_subreddits
        scrape_all_subreddits()
    except Exception as e:
        print(f"Error running Reddit scraper: {e}")
    
    # Amazon scraper
    print("\n[2/4] Amazon Scraper")
    try:
        from scraper.amazon_scraper import scrape_amazon_reviews
        scrape_amazon_reviews()
    except Exception as e:
        print(f"Error running Amazon scraper: {e}")
    
    # YouTube scraper
    print("\n[3/4] YouTube Scraper")
    try:
        from scraper.youtube_scraper import scrape_youtube_comments
        scrape_youtube_comments()
    except Exception as e:
        print(f"Error running YouTube scraper: {e}")
    
    # Forum scraper
    print("\n[4/4] Forum Scraper")
    try:
        from scraper.forum_scraper import scrape_all_forums
        scrape_all_forums()
    except Exception as e:
        print(f"Error running Forum scraper: {e}")


def run_analyzers():
    """Run all data analyzers."""
    print("\n" + "="*70)
    print("RUNNING DATA ANALYZERS")
    print("="*70)
    
    # Sentiment analysis and accessory extraction
    print("\n[1/2] Sentiment Analysis & Accessory Extraction")
    try:
        from analyzer.sentiment import analyze_all_reviews
        analyze_all_reviews()
    except Exception as e:
        print(f"Error running sentiment analysis: {e}")
    
    # Comfort issue categorization
    print("\n[2/2] Comfort Issue Categorization")
    try:
        from analyzer.categorizer import categorize_all_reviews
        categorize_all_reviews()
    except Exception as e:
        print(f"Error running categorizer: {e}")


def print_summary():
    """Print a summary of the collected data."""
    from backend.database import get_connection
    
    conn = get_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("DATA COLLECTION SUMMARY")
    print("="*70)
    
    # Count reviews by source
    cursor.execute("""
        SELECT s.name, COUNT(r.id) as count
        FROM sources s
        LEFT JOIN reviews r ON s.id = r.source_id
        GROUP BY s.id
        ORDER BY count DESC
    """)
    
    print("\nReviews by Source:")
    total_reviews = 0
    for row in cursor.fetchall():
        print(f"  {row['name']}: {row['count']}")
        total_reviews += row['count']
    print(f"  Total: {total_reviews}")
    
    # Count accessory mentions
    cursor.execute("SELECT COUNT(*) as count FROM accessory_mentions")
    mentions = cursor.fetchone()['count']
    print(f"\nAccessory Mentions: {mentions}")
    
    # Count unique accessories
    cursor.execute("SELECT COUNT(DISTINCT accessory_name) as count FROM accessory_mentions")
    unique = cursor.fetchone()['count']
    print(f"Unique Accessories: {unique}")
    
    # Count comfort issues
    cursor.execute("SELECT COUNT(*) as count FROM comfort_issues")
    issues = cursor.fetchone()['count']
    print(f"Comfort Issues Found: {issues}")
    
    # Top accessories
    cursor.execute("""
        SELECT accessory_name, COUNT(*) as count, AVG(sentiment_score) as sentiment
        FROM accessory_mentions
        GROUP BY accessory_name
        ORDER BY count DESC
        LIMIT 5
    """)
    
    print("\nTop 5 Most Mentioned Accessories:")
    for row in cursor.fetchall():
        sentiment = row['sentiment']
        sentiment_str = f"+{sentiment:.2f}" if sentiment > 0 else f"{sentiment:.2f}"
        print(f"  {row['accessory_name']}: {row['count']} mentions ({sentiment_str} sentiment)")
    
    conn.close()
    
    print("\n" + "="*70)
    print("Data collection complete!")
    print("Start the backend: uvicorn backend.main:app --reload")
    print("Start the frontend: cd frontend && npm install && npm run dev")
    print("="*70)


def main():
    parser = argparse.ArgumentParser(
        description="Quest 3 Comfort Analyzer - Data Collection Script"
    )
    parser.add_argument(
        '--scrape', 
        action='store_true',
        help='Only run web scrapers'
    )
    parser.add_argument(
        '--analyze',
        action='store_true', 
        help='Only run data analyzers'
    )
    parser.add_argument(
        '--init-db',
        action='store_true',
        help='Only initialize the database'
    )
    
    args = parser.parse_args()
    
    print("="*70)
    print("Quest 3 Comfort Analyzer - Data Collection")
    print("="*70)
    
    # Always ensure database is initialized
    print("\nInitializing database...")
    init_database()
    
    if args.init_db:
        return
    
    if args.scrape:
        run_scrapers()
    elif args.analyze:
        run_analyzers()
    else:
        # Run everything
        run_scrapers()
        run_analyzers()
    
    print_summary()


if __name__ == "__main__":
    main()
