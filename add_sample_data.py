"""Add sample data to the database for testing."""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

sys.path.insert(0, str(Path(__file__).parent))

from backend.database import (
    init_database, insert_review, insert_accessory_mention,
    insert_comfort_issue, get_connection
)

# Sample reviews data
SAMPLE_REVIEWS = [
    {
        "source": "reddit",
        "title": "BoboVR M3 Pro is a game changer!",
        "content": "Just got the BoboVR M3 Pro and it's incredibly comfortable. The weight distribution is perfect and I can play for hours without any forehead pressure. The battery pack acts as a great counterweight. Highly recommend!",
        "upvotes": 245,
        "accessories": [("BoboVR M3 Pro", "head_strap", 0.85)],
        "issues": []
    },
    {
        "source": "reddit",
        "title": "Kiwi Elite Strap Review - Pretty Good",
        "content": "The Kiwi Elite Strap is comfortable and well built. Much better than stock strap. Only downside is the forehead padding could be thicker. After about 2 hours I start to feel some pressure. Overall 8/10.",
        "upvotes": 89,
        "accessories": [("Kiwi Design Elite Strap", "head_strap", 0.45)],
        "issues": [("forehead_discomfort", "low")]
    },
    {
        "source": "reddit",
        "title": "Quest 3 comfort comparison - Best straps tested",
        "content": "Tested BoboVR M3 Pro, Kiwi Elite, Meta Elite Strap, and AMVR. BoboVR is the clear winner for comfort. Meta Elite Strap looks premium but broke after 2 months. Kiwi is great value. AMVR is decent for the price.",
        "upvotes": 567,
        "accessories": [
            ("BoboVR M3 Pro", "head_strap", 0.9),
            ("Kiwi Design Elite Strap", "head_strap", 0.6),
            ("Meta Elite Strap", "head_strap", 0.2),
            ("AMVR Head Strap", "head_strap", 0.4)
        ],
        "issues": [("strap_quality", "high")]
    },
    {
        "source": "amazon",
        "title": "VR Cover face interface - Must have!",
        "content": "The VR Cover face interface is so much better than stock. More comfortable, blocks light leaks, and easy to clean. If you sweat during VR workouts this is essential.",
        "upvotes": 156,
        "accessories": [("VR Cover", "face_cover", 0.75)],
        "issues": [("heat_sweating", "medium")]
    },
    {
        "source": "reddit",
        "title": "Quest 3 too heavy - solutions?",
        "content": "The Quest 3 feels really front heavy and uncomfortable. After 30 minutes my forehead hurts. I've tried adjusting the straps but nothing helps. Should I get a halo strap?",
        "upvotes": 34,
        "accessories": [],
        "issues": [("weight", "high"), ("forehead_discomfort", "high")]
    },
    {
        "source": "youtube",
        "title": "Comment on: Quest 3 Best Accessories Guide",
        "content": "Got the BoboVR M3 Pro based on this video and it's amazing. The battery counterweight makes such a difference. No more neck pain!",
        "upvotes": 23,
        "accessories": [("BoboVR M3 Pro", "head_strap", 0.8), ("BoboVR Battery Pack", "battery", 0.7)],
        "issues": []
    },
    {
        "source": "reddit",
        "title": "Prescription lens inserts recommendation",
        "content": "VR Optician prescription lenses are expensive but worth it. Much better than wearing glasses in VR. ZenGuard protectors are also good for keeping dust off.",
        "upvotes": 112,
        "accessories": [("VR Optician", "lens", 0.7), ("ZenGuard Lens Protector", "lens", 0.5)],
        "issues": [("glasses_compatibility", "medium")]
    },
    {
        "source": "reddit",
        "title": "AMVR face cover for fitness - great for Beat Saber",
        "content": "The AMVR silicone face cover is perfect for workouts. Easy to wipe down after sweaty Beat Saber sessions. Stock foam absorbs too much sweat.",
        "upvotes": 78,
        "accessories": [("AMVR Face Cover", "face_cover", 0.65)],
        "issues": [("heat_sweating", "low")]
    },
    {
        "source": "amazon",
        "title": "Meta Elite Battery Strap - Mixed feelings",
        "content": "The Meta Elite Battery Strap is well made but very expensive. Battery life is great but comfort is just okay. For the same price you could get BoboVR M3 Pro plus extras.",
        "upvotes": 45,
        "accessories": [("Meta Elite Battery Strap", "battery", 0.35), ("BoboVR M3 Pro", "head_strap", 0.7)],
        "issues": []
    },
    {
        "source": "reddit",
        "title": "Long gaming sessions - what helps?",
        "content": "For marathon VR sessions I recommend: good head strap (BoboVR), silicone face cover (wipe sweat), counterweight battery. Take breaks every hour. Proper fit matters most.",
        "upvotes": 234,
        "accessories": [
            ("BoboVR M3 Pro", "head_strap", 0.8),
            ("Silicone Face Cover", "face_cover", 0.6)
        ],
        "issues": [("long_session", "medium")]
    },
    {
        "source": "youtube",
        "title": "Comment on: Quest 3 Comfort Mods",
        "content": "The halo strap design really helps distribute weight to the top of your head instead of your face. Game changer for comfort.",
        "upvotes": 56,
        "accessories": [("Halo Strap", "head_strap", 0.7)],
        "issues": [("pressure_points", "low")]
    },
    {
        "source": "reddit",
        "title": "Face interface causing red marks",
        "content": "Stock face interface leaves red marks on my cheeks and forehead. Anyone else have this issue? Looking for alternatives that don't dig in so much.",
        "upvotes": 67,
        "accessories": [],
        "issues": [("pressure_points", "medium"), ("face_interface", "medium")]
    },
    {
        "source": "amazon",
        "title": "DESTEK Head Strap - Budget option review",
        "content": "DESTEK strap is decent for the price. Not as comfortable as BoboVR but much better than stock. Good if you're on a budget.",
        "upvotes": 34,
        "accessories": [("DESTEK Head Strap", "head_strap", 0.4), ("BoboVR M3 Pro", "head_strap", 0.6)],
        "issues": []
    },
    {
        "source": "reddit",
        "title": "Quest 3 gets too hot during workouts",
        "content": "Playing fitness games like Beat Saber makes the Quest 3 fog up and get really hot. Face gets sweaty fast. Need better ventilation.",
        "upvotes": 89,
        "accessories": [],
        "issues": [("heat_sweating", "high")]
    },
    {
        "source": "reddit",
        "title": "Controller grips are a must",
        "content": "Kiwi controller grips changed how I play. No more worrying about throwing my controllers during Beat Saber. Much more secure feeling.",
        "upvotes": 123,
        "accessories": [("Kiwi Controller Grips", "controller", 0.75)],
        "issues": []
    }
]

def add_sample_data():
    """Add sample data to database."""
    print("Adding sample data to database...")
    
    init_database()
    
    base_date = datetime.now() - timedelta(days=30)
    
    for i, review_data in enumerate(SAMPLE_REVIEWS):
        # Insert review
        date_posted = base_date + timedelta(days=i, hours=random.randint(0, 23))
        
        review_id = insert_review(
            source_name=review_data["source"],
            external_id=f"sample_{i}",
            title=review_data["title"],
            content=review_data["content"],
            author=f"user_{random.randint(1000, 9999)}",
            date_posted=date_posted,
            upvotes=review_data["upvotes"],
            url=f"https://example.com/review/{i}"
        )
        
        if review_id:
            # Insert accessory mentions
            for name, acc_type, sentiment in review_data["accessories"]:
                insert_accessory_mention(
                    review_id=review_id,
                    accessory_name=name,
                    accessory_type=acc_type,
                    sentiment_score=sentiment + random.uniform(-0.1, 0.1),
                    context_snippet=review_data["content"][:300]
                )
            
            # Insert comfort issues
            for issue_type, severity in review_data["issues"]:
                insert_comfort_issue(
                    review_id=review_id,
                    issue_type=issue_type,
                    severity=severity,
                    context_snippet=review_data["content"][:300]
                )
    
    # Print summary
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM reviews")
    review_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM accessory_mentions")
    mention_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM comfort_issues")
    issue_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\nSample data added:")
    print(f"  Reviews: {review_count}")
    print(f"  Accessory mentions: {mention_count}")
    print(f"  Comfort issues: {issue_count}")
    print("\nYou can now start the backend and frontend to view the dashboard!")

if __name__ == "__main__":
    add_sample_data()
