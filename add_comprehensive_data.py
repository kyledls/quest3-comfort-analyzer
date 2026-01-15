"""Add comprehensive sample data to demonstrate the dashboard with realistic data volumes."""

import sys
import random
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from backend.database import (
    init_database, get_connection, insert_review, 
    insert_accessory_mention, insert_comfort_issue
)

# Comprehensive review templates
REVIEW_TEMPLATES = {
    "head_strap": {
        "BoboVR M3 Pro": {
            "positive": [
                "The BoboVR M3 Pro is hands down the best strap for Quest 3. Perfect weight distribution and the battery counterweight is genius.",
                "Finally comfortable for long sessions! BoboVR M3 Pro solved all my comfort issues. No more forehead pain.",
                "Got the BoboVR M3 Pro last week. Game changer. Can play for 3+ hours now without discomfort.",
                "M3 Pro is worth every penny. The halo design takes pressure off your face completely.",
                "Best purchase for my Quest 3. BoboVR nailed it with the M3 Pro design.",
                "Upgraded from stock strap to BoboVR M3 Pro. Night and day difference in comfort.",
                "The BoboVR battery pack as counterweight makes the Quest 3 feel weightless.",
                "M3 Pro comfort is incredible. My wife can finally enjoy VR without complaints.",
            ],
            "negative": [
                "BoboVR M3 Pro is good but the top strap digs in after about 2 hours.",
                "M3 Pro plastic feels a bit cheap for the price. Hope it doesn't break.",
            ]
        },
        "Kiwi Design Elite Strap": {
            "positive": [
                "Kiwi Elite Strap is excellent value. Almost as good as BoboVR at half the price.",
                "Really happy with my Kiwi strap purchase. Solid build quality and comfortable.",
                "Kiwi Design makes great accessories. Their elite strap is a solid choice.",
                "The Kiwi elite strap adjustment dial is smooth and holds position well.",
                "Good alternative to Meta's overpriced elite strap. Kiwi does the job well.",
            ],
            "negative": [
                "Kiwi strap is decent but forehead padding could be thicker.",
                "My Kiwi strap creaks a bit when adjusting. Minor annoyance.",
            ]
        },
        "Meta Elite Strap": {
            "positive": [
                "Meta Elite Strap looks premium and fits perfectly. You get what you pay for.",
                "Official Meta strap has the best fit of any I've tried.",
            ],
            "negative": [
                "Meta Elite Strap broke after 3 months. Same issue as Quest 2 version. Avoid!",
                "Way overpriced for what it is. Meta Elite Strap cracked at the hinge.",
                "Don't buy Meta's elite strap. Mine snapped. Known defect they won't fix.",
                "Elite strap durability is terrible. Third party options are better.",
                "Returned my Meta Elite Strap after reading about all the breakage issues.",
            ]
        },
        "AMVR Head Strap": {
            "positive": [
                "AMVR strap is budget friendly and gets the job done. Good starter upgrade.",
                "Decent strap for the price. AMVR is a good entry point.",
                "AMVR head strap works well enough. Can't complain for $30.",
            ],
            "negative": [
                "AMVR strap is okay but feels cheap. Upgraded to BoboVR after a month.",
                "Not the most comfortable but AMVR works if you're on a tight budget.",
            ]
        },
        "DESTEK Head Strap": {
            "positive": [
                "DESTEK strap surprised me. Better than expected for a budget option.",
                "Good value with the DESTEK strap. Comfortable enough for casual use.",
            ],
            "negative": [
                "DESTEK quality is hit or miss. Mine had loose stitching.",
            ]
        },
        "Halo Strap": {
            "positive": [
                "Halo style straps are the way to go. Takes all pressure off your face.",
                "Love my halo strap. Weight sits on top of head instead of face.",
                "The halo design is so much better than the stock strap style.",
            ],
            "negative": []
        },
    },
    "face_cover": {
        "VR Cover": {
            "positive": [
                "VR Cover face interface is a must buy. Blocks all light leaks and so comfy.",
                "Best face cover money can buy. VR Cover quality is top notch.",
                "VR Cover PU leather is easy to clean after sweaty sessions.",
                "Upgraded to VR Cover and never looking back. Premium feel.",
                "The VR Cover padding is much better than stock foam.",
            ],
            "negative": [
                "VR Cover is pricey but you get what you pay for.",
            ]
        },
        "AMVR Face Cover": {
            "positive": [
                "AMVR silicone face cover is perfect for Beat Saber workouts.",
                "Easy to wipe down after sweating. AMVR silicone is great.",
                "AMVR face interface fits well and blocks light.",
            ],
            "negative": [
                "AMVR silicone can feel sticky on hot days.",
            ]
        },
        "Kiwi Face Interface": {
            "positive": [
                "Kiwi face interface is comfortable and good value.",
                "Nice upgrade from stock. Kiwi face cover is solid.",
            ],
            "negative": []
        },
        "Silicone Face Cover": {
            "positive": [
                "Silicone covers are essential for VR fitness. Easy to clean!",
                "Generic silicone cover works great for sweaty sessions.",
                "Silicone face covers are a cheap must-have accessory.",
            ],
            "negative": [
                "Silicone can get uncomfortable during long sessions.",
            ]
        },
    },
    "battery": {
        "BoboVR Battery Pack": {
            "positive": [
                "BoboVR battery pack doubles as perfect counterweight. Genius design.",
                "Love how the BoboVR battery balances the headset. So comfortable.",
                "Battery life extended and comfort improved. BoboVR battery is a win-win.",
            ],
            "negative": []
        },
        "Meta Elite Battery Strap": {
            "positive": [
                "Meta battery strap is convenient. Charges while you play.",
            ],
            "negative": [
                "Way too expensive for what it is. Meta Elite Battery is overpriced.",
                "Same durability issues as regular elite strap. Avoid the Meta battery version.",
            ]
        },
        "Anker Power Bank": {
            "positive": [
                "Velcro an Anker battery to the back strap. Cheap counterweight solution.",
                "Anker power bank works great as DIY counterweight and extended battery.",
            ],
            "negative": []
        },
    },
    "lens": {
        "VR Optician": {
            "positive": [
                "VR Optician prescription lenses are crystal clear. Worth the investment.",
                "Best prescription lens option. VR Optician quality is excellent.",
                "Finally can use VR without glasses! VR Optician lenses are perfect.",
            ],
            "negative": [
                "VR Optician is expensive but the quality justifies it.",
            ]
        },
        "ZenGuard Lens Protector": {
            "positive": [
                "ZenGuard protectors keep my lenses safe from scratches.",
                "Cheap insurance. ZenGuard lens covers work well.",
            ],
            "negative": []
        },
        "Prescription Lens Insert": {
            "positive": [
                "Prescription inserts changed VR for me. No more glasses discomfort.",
                "Highly recommend prescription lens inserts if you wear glasses.",
            ],
            "negative": []
        },
    },
    "controller": {
        "Kiwi Controller Grips": {
            "positive": [
                "Kiwi controller grips are amazing for Beat Saber. No more flying controllers!",
                "Secure grip with Kiwi straps. Essential for active games.",
                "Love my Kiwi grips. Controllers feel more secure now.",
            ],
            "negative": []
        },
        "Controller Grips": {
            "positive": [
                "Controller grips are a must for fitness games. Much more secure.",
                "Knuckle straps make such a difference in confidence while playing.",
            ],
            "negative": []
        },
    }
}

# Comfort issue templates
COMFORT_ISSUES = {
    "weight": {
        "high": [
            "Quest 3 is way too front heavy. After 20 minutes my neck is killing me.",
            "The weight distribution is terrible on stock strap. Need a counterweight.",
            "Can't play for more than 30 mins. The front heavy design is exhausting.",
            "My neck hurts so bad after VR. The Quest 3 weight is brutal.",
            "Front heavy headset is ruining my VR experience. Need solutions.",
        ],
        "medium": [
            "Quest 3 is heavier than Quest 2. Takes some getting used to.",
            "Weight is noticeable but manageable with a good strap.",
            "Definitely front heavy but a counterweight helps a lot.",
        ],
        "low": [
            "Weight isn't too bad once you get the strap adjusted right.",
            "Slight front heaviness but not a dealbreaker.",
        ]
    },
    "pressure_points": {
        "high": [
            "Stock face interface creates painful pressure points on my cheeks.",
            "Red marks all over my face after 30 minutes. This is unacceptable.",
            "The pressure on my forehead and cheekbones is unbearable.",
            "Can't use Quest 3 because of the painful pressure. Need help!",
        ],
        "medium": [
            "Some pressure on cheekbones but tolerable with breaks.",
            "Face interface digs in a bit. Looking for alternatives.",
            "Pressure points are annoying but not terrible.",
            "Leaves some marks on my face but they fade quickly.",
        ],
        "low": [
            "Minor pressure but adjusting the strap helped.",
            "Slight pressure point on nose bridge.",
        ]
    },
    "forehead_discomfort": {
        "high": [
            "Extreme forehead pain after just 15 minutes. Stock strap is terrible.",
            "My forehead is sore for hours after playing. Can't take it anymore.",
            "The pressure on my forehead is giving me headaches.",
        ],
        "medium": [
            "Forehead gets sore after about an hour of play.",
            "Some discomfort on forehead but halo straps help a lot.",
            "Forehead pain is manageable with good padding.",
            "Mild forehead pressure but better with aftermarket strap.",
        ],
        "low": [
            "Slight forehead sensation but nothing major.",
            "Forehead comfort improved after adjusting angle.",
        ]
    },
    "heat_sweating": {
        "high": [
            "Quest 3 gets SO hot during Beat Saber. Lens fog up constantly.",
            "Sweating buckets after 10 mins of VR fitness. Need better ventilation.",
            "The heat buildup is insane. Can't do cardio games anymore.",
            "Face is drenched in sweat. Stock foam absorbs everything. Gross.",
            "Overheating is ruining my workout VR sessions.",
        ],
        "medium": [
            "Gets warm during active games. Silicone covers help with cleanup.",
            "Some fogging issues but not too bad with breaks.",
            "Sweating is an issue but silicone face covers make cleaning easy.",
            "Heat is noticeable during intense games.",
            "Taking short breaks helps with the heat buildup.",
        ],
        "low": [
            "Slight warmth but not uncomfortable.",
            "Minor sweating during long sessions.",
        ]
    },
    "face_interface": {
        "high": [
            "Stock face interface is garbage. Light leaks everywhere.",
            "The foam face cover is cheap and uncomfortable. Needs replacement.",
        ],
        "medium": [
            "Stock face interface is okay but aftermarket is much better.",
            "Some light leak at the nose. Looking for better face cover.",
            "Face interface could use more padding.",
            "Default face cover isn't great for my face shape.",
        ],
        "low": [
            "Face interface is fine but could be improved.",
        ]
    },
    "strap_quality": {
        "high": [
            "Stock strap is absolute garbage. Flimsy and uncomfortable.",
            "My elite strap broke after 2 months! Total waste of money.",
            "Strap snapped during normal use. Terrible quality control.",
        ],
        "medium": [
            "Stock strap is usable but definitely needs upgrading.",
            "Strap adjustment is finicky. Third party options are better.",
            "Build quality on stock strap feels cheap.",
        ],
        "low": [
            "Stock strap works but aftermarket is more comfortable.",
        ]
    },
    "fit_adjustment": {
        "high": [
            "Can't get a good fit no matter how much I adjust. Frustrating!",
            "The strap keeps slipping. Nothing stays in place.",
        ],
        "medium": [
            "Takes a while to dial in the perfect fit.",
            "Fit adjustment is tricky but worth the effort.",
            "Straps need frequent readjustment.",
        ],
        "low": [
            "Fit is decent once you figure out the adjustments.",
        ]
    },
    "glasses_compatibility": {
        "high": [
            "Can't wear my glasses in Quest 3. They don't fit!",
            "Glasses scratch the lenses. Need prescription inserts ASAP.",
        ],
        "medium": [
            "Glasses fit but it's tight. Prescription lenses recommended.",
            "Using glasses spacer but it's not ideal.",
            "IPD adjustment helps with glasses but still uncomfortable.",
        ],
        "low": [
            "Small glasses work fine. Larger frames might have issues.",
        ]
    },
    "long_session": {
        "high": [
            "Can't play for more than 30 mins without pain. Unacceptable.",
            "Extended VR sessions are impossible with stock setup.",
        ],
        "medium": [
            "After 1-2 hours I need a break. Face gets tired.",
            "Long sessions are tiring but manageable with good accessories.",
            "Can do about an hour before needing to rest.",
            "Extended play requires breaks every 45 minutes or so.",
        ],
        "low": [
            "Can play for hours with the right strap and face cover.",
            "Long sessions are fine after upgrading accessories.",
        ]
    },
    "battery_weight": {
        "high": [],
        "medium": [
            "Battery pack adds weight but improves balance.",
            "The added battery weight actually helps with comfort.",
        ],
        "low": [
            "Battery as counterweight is genius. Better than stock balance.",
            "Weight from battery pack makes headset more comfortable.",
        ]
    }
}

def add_comprehensive_data():
    """Add comprehensive sample data."""
    print("Adding comprehensive data to database...")
    
    init_database()
    conn = get_connection()
    cursor = conn.cursor()
    
    # Clear existing sample data
    cursor.execute("DELETE FROM comfort_issues")
    cursor.execute("DELETE FROM accessory_mentions")
    cursor.execute("DELETE FROM reviews WHERE external_id LIKE 'sample_%' OR external_id LIKE 'comp_%'")
    conn.commit()
    
    base_date = datetime.now() - timedelta(days=90)
    review_count = 0
    mention_count = 0
    issue_count = 0
    
    sources = ["reddit", "reddit", "reddit", "amazon", "youtube", "reddit"]  # Weighted towards Reddit
    
    # Add accessory reviews
    print("\nAdding accessory reviews...")
    for acc_type, accessories in REVIEW_TEMPLATES.items():
        for acc_name, sentiments in accessories.items():
            # Add positive reviews
            for i, review_text in enumerate(sentiments["positive"]):
                source = random.choice(sources)
                date = base_date + timedelta(days=random.randint(0, 90), hours=random.randint(0, 23))
                upvotes = random.randint(10, 500) if random.random() > 0.3 else random.randint(1, 50)
                
                review_id = insert_review(
                    source_name=source,
                    external_id=f"comp_acc_{acc_name}_{i}",
                    title=f"{acc_name} Review",
                    content=review_text,
                    author=f"user_{random.randint(1000, 99999)}",
                    date_posted=date,
                    upvotes=upvotes,
                    url=f"https://example.com/{source}/{review_count}"
                )
                
                if review_id:
                    review_count += 1
                    sentiment = random.uniform(0.5, 0.95)
                    insert_accessory_mention(
                        review_id=review_id,
                        accessory_name=acc_name,
                        accessory_type=acc_type,
                        sentiment_score=sentiment,
                        context_snippet=review_text
                    )
                    mention_count += 1
            
            # Add negative reviews
            for i, review_text in enumerate(sentiments["negative"]):
                source = random.choice(sources)
                date = base_date + timedelta(days=random.randint(0, 90))
                upvotes = random.randint(5, 200)
                
                review_id = insert_review(
                    source_name=source,
                    external_id=f"comp_acc_neg_{acc_name}_{i}",
                    title=f"{acc_name} Issues",
                    content=review_text,
                    author=f"user_{random.randint(1000, 99999)}",
                    date_posted=date,
                    upvotes=upvotes,
                    url=f"https://example.com/{source}/{review_count}"
                )
                
                if review_id:
                    review_count += 1
                    sentiment = random.uniform(-0.6, 0.1)
                    insert_accessory_mention(
                        review_id=review_id,
                        accessory_name=acc_name,
                        accessory_type=acc_type,
                        sentiment_score=sentiment,
                        context_snippet=review_text
                    )
                    mention_count += 1
    
    # Add comfort issue reviews
    print("Adding comfort issue reviews...")
    for issue_type, severities in COMFORT_ISSUES.items():
        for severity, complaints in severities.items():
            for i, complaint_text in enumerate(complaints):
                source = random.choice(sources)
                date = base_date + timedelta(days=random.randint(0, 90))
                upvotes = random.randint(20, 300) if severity == "high" else random.randint(5, 100)
                
                review_id = insert_review(
                    source_name=source,
                    external_id=f"comp_issue_{issue_type}_{severity}_{i}",
                    title=f"Quest 3 {issue_type.replace('_', ' ').title()} Issue",
                    content=complaint_text,
                    author=f"user_{random.randint(1000, 99999)}",
                    date_posted=date,
                    upvotes=upvotes,
                    url=f"https://example.com/{source}/{review_count}"
                )
                
                if review_id:
                    review_count += 1
                    insert_comfort_issue(
                        review_id=review_id,
                        issue_type=issue_type,
                        severity=severity,
                        context_snippet=complaint_text
                    )
                    issue_count += 1
    
    # Add some mixed reviews that mention multiple accessories and issues
    print("Adding mixed reviews...")
    mixed_reviews = [
        {
            "content": "Upgraded my Quest 3 with BoboVR M3 Pro and VR Cover face interface. The difference is night and day! No more forehead pain and I can play for hours. The battery counterweight is genius. Heat is still an issue during Beat Saber but silicone covers help.",
            "accessories": [("BoboVR M3 Pro", "head_strap", 0.9), ("VR Cover", "face_cover", 0.85)],
            "issues": [("heat_sweating", "medium"), ("forehead_discomfort", "low")]
        },
        {
            "content": "Compared BoboVR M3 Pro vs Kiwi Elite vs Meta Elite. BoboVR wins for comfort, Kiwi is best value, Meta is overpriced and breaks. All are better than stock strap which gave me terrible pressure points.",
            "accessories": [("BoboVR M3 Pro", "head_strap", 0.85), ("Kiwi Design Elite Strap", "head_strap", 0.7), ("Meta Elite Strap", "head_strap", 0.2)],
            "issues": [("pressure_points", "high"), ("strap_quality", "high")]
        },
        {
            "content": "Quest 3 comfort guide: 1) Get a halo strap like BoboVR 2) Add battery for counterweight 3) Replace face interface 4) Take breaks. Weight distribution is the key to long sessions.",
            "accessories": [("BoboVR M3 Pro", "head_strap", 0.9), ("BoboVR Battery Pack", "battery", 0.85)],
            "issues": [("weight", "medium"), ("long_session", "low")]
        },
        {
            "content": "VR Optician prescription lenses are a game changer. No more uncomfortable glasses squishing against my face. Combined with AMVR face cover, Quest 3 is finally comfortable.",
            "accessories": [("VR Optician", "lens", 0.9), ("AMVR Face Cover", "face_cover", 0.75)],
            "issues": [("glasses_compatibility", "low")]
        },
        {
            "content": "Beat Saber setup: Kiwi controller grips (essential!), silicone face cover for sweat, and good head strap. The stock setup is unbearable for fitness games.",
            "accessories": [("Kiwi Controller Grips", "controller", 0.9), ("Silicone Face Cover", "face_cover", 0.8)],
            "issues": [("heat_sweating", "medium")]
        },
    ]
    
    for i, review in enumerate(mixed_reviews):
        for _ in range(3):  # Add each mixed review multiple times with variations
            source = random.choice(sources)
            date = base_date + timedelta(days=random.randint(0, 90))
            upvotes = random.randint(50, 800)
            
            review_id = insert_review(
                source_name=source,
                external_id=f"comp_mixed_{i}_{_}",
                title="Quest 3 Comfort Setup",
                content=review["content"],
                author=f"user_{random.randint(1000, 99999)}",
                date_posted=date,
                upvotes=upvotes,
                url=f"https://example.com/{source}/mixed_{review_count}"
            )
            
            if review_id:
                review_count += 1
                for acc_name, acc_type, sentiment in review["accessories"]:
                    insert_accessory_mention(
                        review_id=review_id,
                        accessory_name=acc_name,
                        accessory_type=acc_type,
                        sentiment_score=sentiment + random.uniform(-0.1, 0.1),
                        context_snippet=review["content"][:300]
                    )
                    mention_count += 1
                
                for issue_type, severity in review["issues"]:
                    insert_comfort_issue(
                        review_id=review_id,
                        issue_type=issue_type,
                        severity=severity,
                        context_snippet=review["content"][:300]
                    )
                    issue_count += 1
    
    conn.close()
    
    # Print summary
    print("\n" + "="*50)
    print("Comprehensive Data Added!")
    print("="*50)
    print(f"Reviews added: {review_count}")
    print(f"Accessory mentions: {mention_count}")
    print(f"Comfort issues: {issue_count}")
    
    # Show breakdown
    conn = get_connection()
    cursor = conn.cursor()
    
    print("\nAccessory Mentions by Type:")
    cursor.execute("""
        SELECT accessory_type, COUNT(*) as count 
        FROM accessory_mentions 
        GROUP BY accessory_type 
        ORDER BY count DESC
    """)
    for row in cursor.fetchall():
        print(f"  {row['accessory_type']}: {row['count']}")
    
    print("\nComfort Issues by Type:")
    cursor.execute("""
        SELECT issue_type, COUNT(*) as count 
        FROM comfort_issues 
        GROUP BY issue_type 
        ORDER BY count DESC
    """)
    for row in cursor.fetchall():
        print(f"  {row['issue_type']}: {row['count']}")
    
    conn.close()
    print("\nRefresh the dashboard to see updated data!")


if __name__ == "__main__":
    add_comprehensive_data()
