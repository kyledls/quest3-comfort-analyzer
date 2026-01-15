"""
Sentiment analysis module for Quest 3 comfort reviews.

Uses TextBlob for basic sentiment analysis and spaCy for NLP.
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tqdm import tqdm

# Try to import NLP libraries
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("Warning: TextBlob not installed. Run: pip install textblob")

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("Warning: spaCy not installed. Run: pip install spacy && python -m spacy download en_core_web_sm")

from backend.database import (
    get_connection, get_all_reviews, 
    insert_accessory_mention
)
from scraper.utils import KNOWN_ACCESSORIES


class SentimentAnalyzer:
    """Analyze sentiment in text using TextBlob and spaCy."""
    
    def __init__(self):
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("spaCy model not found. Run: python -m spacy download en_core_web_sm")
    
    def analyze_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of text.
        Returns a score between -1 (negative) and 1 (positive).
        """
        if not text or not TEXTBLOB_AVAILABLE:
            return 0.0
        
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except:
            return 0.0
    
    def analyze_sentiment_around_term(self, text: str, term: str, window: int = 50) -> float:
        """
        Analyze sentiment specifically around a mentioned term.
        This gives more accurate sentiment for specific accessory mentions.
        """
        if not text or not term:
            return self.analyze_sentiment(text)
        
        text_lower = text.lower()
        term_lower = term.lower()
        
        # Find all occurrences of the term
        start = 0
        snippets = []
        
        while True:
            idx = text_lower.find(term_lower, start)
            if idx == -1:
                break
            
            # Extract context window around the term
            snippet_start = max(0, idx - window)
            snippet_end = min(len(text), idx + len(term) + window)
            snippet = text[snippet_start:snippet_end]
            snippets.append(snippet)
            
            start = idx + 1
        
        if not snippets:
            return self.analyze_sentiment(text)
        
        # Average sentiment across all mentions
        sentiments = [self.analyze_sentiment(s) for s in snippets]
        return sum(sentiments) / len(sentiments)
    
    def get_key_phrases(self, text: str) -> List[str]:
        """Extract key noun phrases from text using spaCy."""
        if not text or not self.nlp:
            return []
        
        try:
            doc = self.nlp(text[:5000])  # Limit text length
            phrases = []
            
            for chunk in doc.noun_chunks:
                phrase = chunk.text.strip().lower()
                if len(phrase) > 2:
                    phrases.append(phrase)
            
            return phrases
        except:
            return []
    
    def extract_opinions(self, text: str) -> List[Dict]:
        """
        Extract opinion phrases (adjective + noun combinations).
        Useful for understanding what people say about accessories.
        """
        if not text or not self.nlp:
            return []
        
        try:
            doc = self.nlp(text[:5000])
            opinions = []
            
            for token in doc:
                # Look for adjectives
                if token.pos_ == "ADJ":
                    # Check if it modifies a noun
                    if token.head.pos_ == "NOUN":
                        opinions.append({
                            "adjective": token.text.lower(),
                            "noun": token.head.text.lower(),
                            "sentiment": self.analyze_sentiment(f"{token.text} {token.head.text}")
                        })
            
            return opinions
        except:
            return []


def find_accessory_mentions(text: str) -> List[Dict]:
    """
    Find mentions of known Quest 3 accessories in text.
    Returns list of dicts with accessory name, type, and context.
    """
    if not text:
        return []
    
    text_lower = text.lower()
    found = []
    
    for accessory_type, patterns in KNOWN_ACCESSORIES.items():
        for pattern in patterns:
            if pattern in text_lower:
                # Find the position and extract context
                idx = text_lower.find(pattern)
                start = max(0, idx - 100)
                end = min(len(text), idx + len(pattern) + 100)
                context = text[start:end].strip()
                
                # Normalize the accessory name
                accessory_name = normalize_accessory_name(pattern)
                
                found.append({
                    "name": accessory_name,
                    "type": accessory_type,
                    "pattern": pattern,
                    "context": context
                })
    
    return found


def normalize_accessory_name(pattern: str) -> str:
    """Normalize accessory pattern to a standard name."""
    normalizations = {
        # Head straps
        "bobo vr": "BoboVR M3 Pro",
        "bobovr": "BoboVR M3 Pro",
        "bobo m3": "BoboVR M3 Pro",
        "m3 pro": "BoboVR M3 Pro",
        "m3pro": "BoboVR M3 Pro",
        "kiwi elite": "Kiwi Design Elite Strap",
        "kiwi strap": "Kiwi Design Elite Strap",
        "kiwi design": "Kiwi Design",
        "elite strap": "Meta Elite Strap",
        "meta elite": "Meta Elite Strap",
        "quest 3 elite": "Meta Elite Strap",
        "amvr strap": "AMVR Head Strap",
        "amvr head": "AMVR Head Strap",
        "destek strap": "DESTEK Head Strap",
        "destek head": "DESTEK Head Strap",
        "globular cluster": "Globular Cluster Strap",
        "halo strap": "Halo Strap",
        "yoges strap": "Yoges Head Strap",
        "eyglo strap": "Eyglo Head Strap",
        "esimen strap": "Esimen Head Strap",
        "aubika strap": "Aubika Head Strap",
        
        # Face covers
        "vr cover": "VR Cover",
        "vrcover": "VR Cover",
        "amvr face": "AMVR Face Cover",
        "amvr facial": "AMVR Face Cover",
        "amvr interface": "AMVR Face Interface",
        "kiwi face": "Kiwi Face Interface",
        "kiwi interface": "Kiwi Face Interface",
        "silicone cover": "Silicone Face Cover",
        "silicone face": "Silicone Face Cover",
        "pu leather": "PU Leather Face Cover",
        "leather face": "PU Leather Face Cover",
        "fitness face": "Fitness Face Cover",
        "workout face": "Workout Face Cover",
        "vrpanda": "VR Panda",
        "vr panda": "VR Panda",
        
        # Batteries
        "bobo battery": "BoboVR Battery Pack",
        "bobovr battery": "BoboVR Battery Pack",
        "m3 battery": "BoboVR M3 Battery",
        "anker": "Anker Power Bank",
        "power bank": "Power Bank",
        "elite battery": "Meta Elite Battery Strap",
        "battery strap": "Battery Strap",
        "rebuff reality": "Rebuff Reality VR Power",
        "vr power": "VR Power",
        "kiwi battery": "Kiwi Battery Pack",
        
        # Lenses
        "zenguard": "ZenGuard Lens Protector",
        "zen guard": "ZenGuard Lens Protector",
        "lens protector": "Lens Protector",
        "prescription lens": "Prescription Lens Insert",
        "prescription insert": "Prescription Lens Insert",
        "vr optician": "VR Optician",
        "vr wave": "VR Wave",
        "widmo": "Widmo Lenses",
        "reloptix": "Reloptix",
        "honsvr": "HonsVR",
        "vr lens lab": "VR Lens Lab",
        
        # Controllers
        "controller grip": "Controller Grips",
        "grips": "Controller Grips",
        "knuckle strap": "Knuckle Straps",
        "hand strap": "Hand Straps",
        "amvr grip": "AMVR Controller Grips",
        "kiwi grip": "Kiwi Controller Grips",
        "controller cover": "Controller Cover",
        "silicone grip": "Silicone Grips",
        
        # Other
        "carrying case": "Carrying Case",
        "travel case": "Travel Case",
        "hard case": "Hard Case",
        "cable management": "Cable Management",
        "pulley system": "Pulley System",
        "fan": "Cooling Fan",
        "cooling fan": "Cooling Fan",
        "freskdesk": "FreskDesk Fan",
        "counterweight": "Counterweight",
        "power adapter": "Power Adapter"
    }
    
    return normalizations.get(pattern.lower(), pattern.title())


def analyze_all_reviews():
    """Analyze all reviews in the database for sentiment and accessory mentions."""
    print("\n" + "="*60)
    print("Sentiment Analysis and Accessory Extraction")
    print("="*60)
    
    analyzer = SentimentAnalyzer()
    reviews = get_all_reviews()
    
    print(f"\nAnalyzing {len(reviews)} reviews...")
    
    total_mentions = 0
    accessory_counts = {}
    
    for review in tqdm(reviews, desc="Processing"):
        # Combine title and content for analysis
        full_text = f"{review.get('title', '')} {review.get('content', '')}"
        
        if not full_text.strip():
            continue
        
        # Find accessory mentions
        mentions = find_accessory_mentions(full_text)
        
        for mention in mentions:
            # Analyze sentiment around this specific mention
            sentiment = analyzer.analyze_sentiment_around_term(
                full_text, 
                mention['pattern']
            )
            
            # Insert into database
            insert_accessory_mention(
                review_id=review['id'],
                accessory_name=mention['name'],
                accessory_type=mention['type'],
                sentiment_score=sentiment,
                context_snippet=mention['context'][:500]
            )
            
            total_mentions += 1
            
            # Track counts
            name = mention['name']
            if name not in accessory_counts:
                accessory_counts[name] = {'count': 0, 'sentiments': []}
            accessory_counts[name]['count'] += 1
            accessory_counts[name]['sentiments'].append(sentiment)
    
    # Print summary
    print("\n" + "-"*60)
    print("Analysis Summary")
    print("-"*60)
    print(f"Total accessory mentions found: {total_mentions}")
    print(f"Unique accessories mentioned: {len(accessory_counts)}")
    
    if accessory_counts:
        print("\nTop Accessories by Mention Count:")
        sorted_accessories = sorted(
            accessory_counts.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:15]
        
        for name, data in sorted_accessories:
            avg_sentiment = sum(data['sentiments']) / len(data['sentiments'])
            sentiment_label = "positive" if avg_sentiment > 0.1 else "negative" if avg_sentiment < -0.1 else "neutral"
            print(f"  {name}: {data['count']} mentions ({sentiment_label}, {avg_sentiment:.2f})")
    
    print("\n" + "="*60)
    print("Sentiment analysis complete!")
    print("="*60)
    
    return total_mentions


if __name__ == "__main__":
    analyze_all_reviews()
