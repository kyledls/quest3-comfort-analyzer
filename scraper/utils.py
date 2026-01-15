"""Utility functions for web scraping."""

import time
import random
import re
from typing import Optional
from fake_useragent import UserAgent

# Initialize user agent rotator
try:
    ua = UserAgent()
except:
    ua = None

# Keywords related to Quest 3 comfort
COMFORT_KEYWORDS = [
    "comfort", "comfortable", "uncomfortable", "weight", "heavy", "light",
    "pressure", "pain", "hurt", "hurts", "ache", "sore", "face", "forehead",
    "cheek", "nose", "strap", "head strap", "elite strap", "halo", "battery",
    "balance", "fit", "fits", "fitting", "tight", "loose", "adjustment",
    "padding", "cushion", "foam", "silicone", "sweat", "sweaty", "hot",
    "heat", "ventilation", "breathable", "glasses", "IPD", "lens"
]

# Known Quest 3 accessories for matching
KNOWN_ACCESSORIES = {
    "head_strap": [
        "bobo vr", "bobovr", "bobo m3", "m3 pro", "m3pro",
        "kiwi elite", "kiwi strap", "kiwi design",
        "elite strap", "meta elite", "quest 3 elite",
        "amvr strap", "amvr head",
        "destek strap", "destek head",
        "globular cluster", "halo strap",
        "yoges strap", "eyglo strap",
        "esimen strap", "aubika strap"
    ],
    "face_cover": [
        "vr cover", "vrcover",
        "amvr face", "amvr facial", "amvr interface",
        "kiwi face", "kiwi interface",
        "silicone cover", "silicone face",
        "pu leather", "leather face",
        "fitness face", "workout face",
        "vrpanda", "vr panda"
    ],
    "battery": [
        "bobo battery", "bobovr battery", "m3 battery",
        "anker", "power bank",
        "elite battery", "battery strap",
        "rebuff reality", "vr power",
        "kiwi battery"
    ],
    "lens": [
        "zenguard", "zen guard", "lens protector",
        "prescription lens", "prescription insert",
        "vr optician", "vr wave", "widmo",
        "reloptix", "honsvr", "vr lens lab"
    ],
    "controller": [
        "controller grip", "grips",
        "knuckle strap", "hand strap",
        "amvr grip", "kiwi grip",
        "controller cover", "silicone grip"
    ],
    "other": [
        "carrying case", "travel case", "hard case",
        "cable management", "pulley system",
        "fan", "cooling fan", "freskdesk",
        "counterweight", "power adapter"
    ]
}


def get_random_user_agent() -> str:
    """Get a random user agent string."""
    if ua:
        return ua.random
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def get_headers() -> dict:
    """Get headers for HTTP requests."""
    return {
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }


def random_delay(min_seconds: float = 2.0, max_seconds: float = 5.0):
    """Add a random delay between requests to be respectful."""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def is_quest3_related(text: str) -> bool:
    """Check if text is related to Quest 3."""
    if not text:
        return False
    text_lower = text.lower()
    quest3_terms = ["quest 3", "quest3", "meta quest 3", "mq3"]
    return any(term in text_lower for term in quest3_terms)


def is_comfort_related(text: str) -> bool:
    """Check if text mentions comfort-related topics."""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in COMFORT_KEYWORDS)


def extract_accessory_mentions(text: str) -> list:
    """Extract mentioned accessories from text."""
    if not text:
        return []
    
    text_lower = text.lower()
    found_accessories = []
    
    for accessory_type, patterns in KNOWN_ACCESSORIES.items():
        for pattern in patterns:
            if pattern in text_lower:
                # Extract a snippet of context around the mention
                idx = text_lower.find(pattern)
                start = max(0, idx - 100)
                end = min(len(text), idx + len(pattern) + 100)
                context = text[start:end].strip()
                
                # Clean up the accessory name
                accessory_name = pattern.title()
                
                found_accessories.append({
                    "name": accessory_name,
                    "type": accessory_type,
                    "context": context
                })
    
    return found_accessories


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s.,!?\'"-]', '', text)
    
    return text.strip()


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to a maximum length while keeping whole words."""
    if not text or len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + "..."
