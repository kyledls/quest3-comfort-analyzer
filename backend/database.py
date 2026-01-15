"""Database setup and models for Quest 3 Comfort Analyzer."""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

DATABASE_PATH = Path(__file__).parent.parent / "data" / "quest3_comfort.db"


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize the database with all required tables."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Sources table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Raw posts/reviews
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER,
            external_id TEXT,
            title TEXT,
            content TEXT,
            author TEXT,
            date_posted DATETIME,
            upvotes INTEGER DEFAULT 0,
            url TEXT,
            scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source_id) REFERENCES sources(id),
            UNIQUE(source_id, external_id)
        )
    """)
    
    # Extracted accessory mentions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accessory_mentions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id INTEGER,
            accessory_name TEXT,
            accessory_type TEXT,
            sentiment_score REAL,
            context_snippet TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (review_id) REFERENCES reviews(id)
        )
    """)
    
    # Common comfort complaints
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comfort_issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id INTEGER,
            issue_type TEXT,
            severity TEXT,
            context_snippet TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (review_id) REFERENCES reviews(id)
        )
    """)
    
    # Create indexes for faster queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_source ON reviews(source_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mentions_review ON accessory_mentions(review_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mentions_accessory ON accessory_mentions(accessory_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_issues_review ON comfort_issues(review_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_issues_type ON comfort_issues(issue_type)")
    
    conn.commit()
    
    # Insert default sources if they don't exist
    default_sources = [
        ("reddit", "https://reddit.com"),
        ("amazon", "https://amazon.com"),
        ("youtube", "https://youtube.com"),
        ("bestbuy", "https://bestbuy.com"),
        ("uploadvr", "https://uploadvr.com"),
        ("roadtovr", "https://roadtovr.com"),
        ("meta_forums", "https://communityforums.atmeta.com"),
    ]
    
    for name, url in default_sources:
        cursor.execute(
            "INSERT OR IGNORE INTO sources (name, url) VALUES (?, ?)",
            (name, url)
        )
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized at {DATABASE_PATH}")


def get_source_id(source_name: str) -> Optional[int]:
    """Get the ID of a source by name."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM sources WHERE name = ?", (source_name,))
    result = cursor.fetchone()
    conn.close()
    return result["id"] if result else None


def insert_review(
    source_name: str,
    external_id: str,
    title: str,
    content: str,
    author: str = None,
    date_posted: datetime = None,
    upvotes: int = 0,
    url: str = None
) -> Optional[int]:
    """Insert a review into the database. Returns the review ID or None if duplicate."""
    source_id = get_source_id(source_name)
    if not source_id:
        print(f"Unknown source: {source_name}")
        return None
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO reviews (source_id, external_id, title, content, author, date_posted, upvotes, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (source_id, external_id, title, content, author, date_posted, upvotes, url))
        conn.commit()
        review_id = cursor.lastrowid
        conn.close()
        return review_id
    except sqlite3.IntegrityError:
        # Duplicate entry
        conn.close()
        return None


def insert_accessory_mention(
    review_id: int,
    accessory_name: str,
    accessory_type: str,
    sentiment_score: float,
    context_snippet: str
):
    """Insert an accessory mention."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO accessory_mentions (review_id, accessory_name, accessory_type, sentiment_score, context_snippet)
        VALUES (?, ?, ?, ?, ?)
    """, (review_id, accessory_name, accessory_type, sentiment_score, context_snippet))
    conn.commit()
    conn.close()


def insert_comfort_issue(
    review_id: int,
    issue_type: str,
    severity: str,
    context_snippet: str
):
    """Insert a comfort issue."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO comfort_issues (review_id, issue_type, severity, context_snippet)
        VALUES (?, ?, ?, ?)
    """, (review_id, issue_type, severity, context_snippet))
    conn.commit()
    conn.close()


def get_all_reviews() -> List[Dict[str, Any]]:
    """Get all reviews for analysis."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, s.name as source_name
        FROM reviews r
        JOIN sources s ON r.source_id = s.id
    """)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_accessory_rankings() -> List[Dict[str, Any]]:
    """Get accessory rankings based on mentions and sentiment."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            accessory_name,
            accessory_type,
            COUNT(*) as mention_count,
            AVG(sentiment_score) as avg_sentiment,
            SUM(CASE WHEN sentiment_score > 0.1 THEN 1 ELSE 0 END) as positive_mentions,
            SUM(CASE WHEN sentiment_score < -0.1 THEN 1 ELSE 0 END) as negative_mentions
        FROM accessory_mentions
        GROUP BY accessory_name
        ORDER BY avg_sentiment DESC, mention_count DESC
    """)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_comfort_issues_breakdown() -> List[Dict[str, Any]]:
    """Get breakdown of comfort issues."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            issue_type,
            COUNT(*) as count,
            severity
        FROM comfort_issues
        GROUP BY issue_type, severity
        ORDER BY count DESC
    """)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_source_distribution() -> List[Dict[str, Any]]:
    """Get distribution of reviews by source."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            s.name as source_name,
            COUNT(r.id) as review_count
        FROM sources s
        LEFT JOIN reviews r ON s.id = r.source_id
        GROUP BY s.id
        ORDER BY review_count DESC
    """)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_accessory_details(accessory_name: str) -> Dict[str, Any]:
    """Get detailed information about a specific accessory."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get basic stats
    cursor.execute("""
        SELECT 
            accessory_name,
            accessory_type,
            COUNT(*) as mention_count,
            AVG(sentiment_score) as avg_sentiment
        FROM accessory_mentions
        WHERE accessory_name = ?
        GROUP BY accessory_name
    """, (accessory_name,))
    stats = dict(cursor.fetchone() or {})
    
    # Get all mentions with context
    cursor.execute("""
        SELECT 
            am.context_snippet,
            am.sentiment_score,
            r.title,
            r.url,
            s.name as source_name
        FROM accessory_mentions am
        JOIN reviews r ON am.review_id = r.id
        JOIN sources s ON r.source_id = s.id
        WHERE am.accessory_name = ?
        ORDER BY am.sentiment_score DESC
    """, (accessory_name,))
    mentions = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "stats": stats,
        "mentions": mentions
    }


if __name__ == "__main__":
    init_database()
