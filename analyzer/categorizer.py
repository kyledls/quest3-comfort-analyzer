"""
Categorizer module for identifying comfort issues in Quest 3 reviews.

Extracts and categorizes comfort complaints and issues from review text.
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tqdm import tqdm

from backend.database import (
    get_connection, get_all_reviews, 
    insert_comfort_issue
)

# Comfort issue categories and their keywords/patterns
COMFORT_ISSUE_PATTERNS = {
    "weight": {
        "keywords": [
            "heavy", "weight", "weighs", "front heavy", "front-heavy",
            "head heavy", "too heavy", "lightweight", "light weight"
        ],
        "patterns": [
            r"(?:too|very|really|quite)\s+heavy",
            r"weight\s+(?:is|feels|seems)",
            r"front.heavy",
            r"not\s+(?:heavy|light)"
        ]
    },
    "pressure_points": {
        "keywords": [
            "pressure", "pressure point", "hurts", "pain", "painful",
            "sore", "ache", "aching", "red marks", "marks on face",
            "digs in", "digging", "indent", "indentation"
        ],
        "patterns": [
            r"pressure\s+(?:point|on|around)",
            r"(?:hurts|pain)\s+(?:my|the)\s+(?:face|forehead|cheeks|nose)",
            r"leaves?\s+(?:marks?|indentation)",
            r"(?:sore|aching)\s+(?:face|forehead|head)"
        ]
    },
    "forehead_discomfort": {
        "keywords": [
            "forehead", "forehead pain", "forehead pressure",
            "forehead ache", "forehead sore"
        ],
        "patterns": [
            r"forehead\s+(?:pain|pressure|hurts|sore|ache)",
            r"(?:pressure|pain|hurts)\s+(?:on|my)\s+forehead"
        ]
    },
    "face_interface": {
        "keywords": [
            "face cover", "face interface", "facial interface",
            "face cushion", "face pad", "face foam",
            "light leak", "light leaking", "nose gap"
        ],
        "patterns": [
            r"face\s+(?:cover|interface|cushion|pad|foam)",
            r"light\s+(?:leak|leaking|bleed)",
            r"nose\s+(?:gap|light)"
        ]
    },
    "strap_quality": {
        "keywords": [
            "strap broke", "strap broken", "cheap strap", "flimsy",
            "broke after", "cracked", "snapped", "durability",
            "build quality", "quality issues"
        ],
        "patterns": [
            r"strap\s+(?:broke|broken|cracked|snapped)",
            r"(?:cheap|flimsy|poor)\s+(?:quality|material|build)",
            r"broke\s+after\s+\d+\s+(?:days?|weeks?|months?)"
        ]
    },
    "fit_adjustment": {
        "keywords": [
            "doesn't fit", "too tight", "too loose", "adjustment",
            "hard to adjust", "slips", "sliding", "won't stay",
            "keeps moving", "unstable"
        ],
        "patterns": [
            r"(?:doesn't|does not|won't|will not)\s+fit",
            r"(?:too|very)\s+(?:tight|loose)",
            r"(?:hard|difficult)\s+to\s+adjust",
            r"(?:keeps?|won't stop)\s+(?:slipping|sliding|moving)"
        ]
    },
    "heat_sweating": {
        "keywords": [
            "hot", "heat", "sweaty", "sweat", "sweating",
            "ventilation", "breathable", "warm", "overheating"
        ],
        "patterns": [
            r"(?:too|very|gets)\s+hot",
            r"(?:sweat|sweaty|sweating)\s+(?:a lot|too much|badly)",
            r"(?:no|poor|bad)\s+ventilation",
            r"face\s+(?:gets?|is)\s+(?:hot|sweaty)"
        ]
    },
    "battery_weight": {
        "keywords": [
            "battery weight", "battery adds", "counterbalance",
            "back heavy", "balance", "balanced", "unbalanced"
        ],
        "patterns": [
            r"battery\s+(?:adds?|weight|heavy)",
            r"(?:good|great|perfect|better)\s+balance",
            r"(?:counter)?balance[sd]?\s+(?:the|weight)"
        ]
    },
    "glasses_compatibility": {
        "keywords": [
            "glasses", "spectacles", "eyeglasses", "prescription",
            "glasses don't fit", "can't wear glasses", "IPD"
        ],
        "patterns": [
            r"(?:wear|use|fit)\s+(?:my\s+)?glasses",
            r"glasses\s+(?:don't|do not|won't)\s+fit",
            r"IPD\s+(?:range|adjustment|issue)"
        ]
    },
    "long_session": {
        "keywords": [
            "long session", "extended use", "after hours",
            "after an hour", "prolonged use", "marathon session"
        ],
        "patterns": [
            r"(?:after|for)\s+\d+\s+(?:hour|hr)s?",
            r"long(?:er)?\s+(?:session|play|use|gaming)",
            r"extended\s+(?:session|use|play)"
        ]
    }
}

# Severity indicators
SEVERITY_INDICATORS = {
    "high": [
        "extremely", "unbearable", "terrible", "awful", "horrible",
        "can't use", "unusable", "returned", "returning", "refund",
        "worst", "very painful", "major issue", "deal breaker"
    ],
    "medium": [
        "uncomfortable", "annoying", "frustrating", "noticeable",
        "bothers", "issue", "problem", "complaint"
    ],
    "low": [
        "slightly", "a bit", "somewhat", "minor", "small",
        "barely", "not too bad", "acceptable", "tolerable"
    ]
}


def detect_severity(text: str) -> str:
    """Detect the severity of a comfort issue from context."""
    text_lower = text.lower()
    
    for severity, indicators in SEVERITY_INDICATORS.items():
        for indicator in indicators:
            if indicator in text_lower:
                return severity
    
    return "medium"  # Default to medium


def find_comfort_issues(text: str) -> List[Dict]:
    """
    Find and categorize comfort issues mentioned in text.
    Returns list of dicts with issue type, severity, and context.
    """
    if not text:
        return []
    
    text_lower = text.lower()
    found_issues = []
    seen_contexts = set()
    
    for issue_type, config in COMFORT_ISSUE_PATTERNS.items():
        # Check keywords
        for keyword in config["keywords"]:
            if keyword in text_lower:
                # Find the position and extract context
                idx = text_lower.find(keyword)
                start = max(0, idx - 100)
                end = min(len(text), idx + len(keyword) + 100)
                context = text[start:end].strip()
                
                # Avoid duplicate contexts
                context_key = f"{issue_type}:{context[:50]}"
                if context_key in seen_contexts:
                    continue
                seen_contexts.add(context_key)
                
                severity = detect_severity(context)
                
                found_issues.append({
                    "type": issue_type,
                    "severity": severity,
                    "context": context,
                    "trigger": keyword
                })
        
        # Check regex patterns
        for pattern in config["patterns"]:
            try:
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    idx = match.start()
                    start = max(0, idx - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end].strip()
                    
                    context_key = f"{issue_type}:{context[:50]}"
                    if context_key in seen_contexts:
                        continue
                    seen_contexts.add(context_key)
                    
                    severity = detect_severity(context)
                    
                    found_issues.append({
                        "type": issue_type,
                        "severity": severity,
                        "context": context,
                        "trigger": match.group()
                    })
            except:
                continue
    
    return found_issues


def categorize_all_reviews():
    """Categorize comfort issues in all reviews."""
    print("\n" + "="*60)
    print("Comfort Issue Categorization")
    print("="*60)
    
    reviews = get_all_reviews()
    
    print(f"\nProcessing {len(reviews)} reviews for comfort issues...")
    
    total_issues = 0
    issue_counts = {}
    severity_counts = {"high": 0, "medium": 0, "low": 0}
    
    for review in tqdm(reviews, desc="Processing"):
        # Combine title and content
        full_text = f"{review.get('title', '')} {review.get('content', '')}"
        
        if not full_text.strip():
            continue
        
        # Find comfort issues
        issues = find_comfort_issues(full_text)
        
        for issue in issues:
            # Insert into database
            insert_comfort_issue(
                review_id=review['id'],
                issue_type=issue['type'],
                severity=issue['severity'],
                context_snippet=issue['context'][:500]
            )
            
            total_issues += 1
            
            # Track counts
            issue_type = issue['type']
            if issue_type not in issue_counts:
                issue_counts[issue_type] = 0
            issue_counts[issue_type] += 1
            
            severity_counts[issue['severity']] += 1
    
    # Print summary
    print("\n" + "-"*60)
    print("Categorization Summary")
    print("-"*60)
    print(f"Total comfort issues found: {total_issues}")
    
    if issue_counts:
        print("\nIssues by Category:")
        sorted_issues = sorted(
            issue_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for issue_type, count in sorted_issues:
            # Format the issue type for display
            display_name = issue_type.replace("_", " ").title()
            print(f"  {display_name}: {count}")
    
    print("\nIssues by Severity:")
    for severity, count in severity_counts.items():
        print(f"  {severity.title()}: {count}")
    
    print("\n" + "="*60)
    print("Categorization complete!")
    print("="*60)
    
    return total_issues


def get_issue_solutions() -> Dict[str, List[str]]:
    """
    Returns known solutions for common comfort issues.
    This data can be used in the dashboard to show recommendations.
    """
    return {
        "weight": [
            "Add a counterweight or battery pack to the back",
            "Use a halo-style strap for better weight distribution",
            "Try the BoboVR M3 Pro with battery for balance"
        ],
        "pressure_points": [
            "Use a wider face interface with more padding",
            "Try a halo strap that distributes weight to top of head",
            "Add extra padding or use VR Cover cushions"
        ],
        "forehead_discomfort": [
            "Adjust the angle of the headset",
            "Use a strap with better forehead padding",
            "Try a halo-style strap to move pressure to crown"
        ],
        "face_interface": [
            "Replace stock face cover with aftermarket option",
            "Try VR Cover or AMVR face interface",
            "Use silicone cover for easier cleaning"
        ],
        "strap_quality": [
            "Invest in a quality third-party strap",
            "BoboVR and Kiwi are known for durability",
            "Avoid the cheapest options - they often break"
        ],
        "fit_adjustment": [
            "Take time to properly adjust all straps",
            "Use a strap with more adjustment points",
            "Consider elite-style straps with dials"
        ],
        "heat_sweating": [
            "Use a silicone face cover for easy cleaning",
            "Take breaks to let the headset cool",
            "Consider a fan accessory like FreskDesk",
            "Use breathable face covers designed for fitness"
        ],
        "battery_weight": [
            "Use battery pack as counterweight on back",
            "BoboVR M3 Pro has integrated battery option",
            "This actually helps balance for many users"
        ],
        "glasses_compatibility": [
            "Get prescription lens inserts",
            "Use a glasses spacer if available",
            "VR Optician and Reloptix make prescription options"
        ],
        "long_session": [
            "Ensure proper weight distribution",
            "Use a well-padded strap",
            "Take regular breaks (every 30-60 minutes)"
        ]
    }


if __name__ == "__main__":
    categorize_all_reviews()
