#!/usr/bin/env python3
"""
Normalize dream database explanations.
Adds 'normalized' and optionally 'normalized_short' fields while preserving originals.
"""

import json
import re
import os
from pathlib import Path
from typing import List, Dict

DREAM_DB_FILE = Path("data/dream_database.json")

def normalize_explanation(explanation: str, word: str) -> str:
    """
    Normalize a single explanation string using rule-based transformations.
    """
    text = explanation.strip()
    
    # Rule 1: Standardize opening - handle various patterns
    word_lower = word.lower()
    
    # Pattern: "For a woman/man/young woman/business man to dream (that)?"
    text = re.sub(
        r'For\s+(a\s+)?(young\s+)?(woman|man|business\s+man)\s+to\s+dream\s+(that\s+)?',
        'To dream that you ',
        text,
        flags=re.IGNORECASE
    )
    
    # Pattern: "For a young woman to [verb]" (when not followed by "dream")
    text = re.sub(
        r'For\s+(a\s+)?(young\s+)?(woman|man)\s+to\s+',
        'To dream that you ',
        text,
        flags=re.IGNORECASE
    )
    
    # Pattern: "To seamen, ..." or "To others, ..."
    text = re.sub(
        r'To\s+seamen,?\s+',
        'This dream can also suggest ',
        text,
        flags=re.IGNORECASE
    )
    text = re.sub(
        r'To\s+others,?\s+',
        'More generally, it suggests ',
        text,
        flags=re.IGNORECASE
    )
    
    # Pattern: "For a business man to dream ..."
    text = re.sub(
        r'For\s+a\s+business\s+man\s+to\s+dream\s+',
        'To dream ',
        text,
        flags=re.IGNORECASE
    )
    
    # Rule 2: Convert third-person to second-person
    # "denotes that she will" -> "suggests you may"
    text = re.sub(
        r'\bdenotes\s+that\s+(she|he)\s+will\b',
        'suggests you may',
        text,
        flags=re.IGNORECASE
    )
    
    # "foretells that he will" -> "suggests you might"
    text = re.sub(
        r'\bforetells\s+that\s+(she|he)\s+will\b',
        'suggests you might',
        text,
        flags=re.IGNORECASE
    )
    
    # "the dreamer will" -> "you may"
    text = re.sub(
        r'\bthe\s+dreamer\s+will\b',
        'you may',
        text,
        flags=re.IGNORECASE
    )
    
    # "her [noun]" -> "your [noun]" (when referring to the dreamer)
    text = re.sub(
        r'\bher\s+(illness|reputation|name|honor|prospects|views|violent\s+illness)\b',
        r'your \1',
        text,
        flags=re.IGNORECASE
    )
    
    # "his [noun]" -> "your [noun]" (when referring to the dreamer)
    text = re.sub(
        r'\bhis\s+(embarrassment|reputation|name|honor|prospects|views)\b',
        r'your \1',
        text,
        flags=re.IGNORECASE
    )
    
    # "she will" -> "you may" (when referring to the dreamer)
    text = re.sub(
        r'\bshe\s+will\s+(yield|incur|besmirch|uphold|converse|get|have|be)\b',
        r'you may \1',
        text,
        flags=re.IGNORECASE
    )
    
    # "he will" -> "you may" (when referring to the dreamer)
    text = re.sub(
        r'\bhe\s+will\s+(be|have|get|make|do)\b',
        r'you may \1',
        text,
        flags=re.IGNORECASE
    )
    
    # "If she/he [verb]" -> "If you [verb]" (when referring to the dreamer)
    text = re.sub(
        r'\bIf\s+(she|he)\s+',
        'If you ',
        text,
        flags=re.IGNORECASE
    )
    
    # Fix common third-person verb forms after "you": "you converses" -> "you converse"
    # Remove 's' from verbs that end in 's' when preceded by "you" (but keep "is", "has", "was")
    text = re.sub(
        r'\byou\s+([a-z]+)s\b(?!\s+(is|has|was|does|goes|says))',
        lambda m: f'you {m.group(1)}' if len(m.group(1)) > 2 else m.group(0),
        text,
        flags=re.IGNORECASE
    )
    
    # Rule 3: Ensure it starts with "To dream" pattern if it doesn't already
    # Most explanations should already start with "To dream", "To see", "To abandon", etc.
    # This is handled by the earlier rules, so we don't need to force it here
    
    # Rule 4: Clean up conditionals - make "If it is" -> "If it appears"
    text = re.sub(
        r'\bIf\s+it\s+is\s+broken\b',
        'If it appears broken',
        text,
        flags=re.IGNORECASE
    )
    text = re.sub(
        r'\bIf\s+you\s+escape\b',
        'If you get away',
        text,
        flags=re.IGNORECASE
    )
    
    # Rule 5: Standardize "denotes" -> "suggests" (more modern)
    text = re.sub(
        r'\bdenotes\s+that\b',
        'suggests that',
        text,
        flags=re.IGNORECASE
    )
    text = re.sub(
        r'\bdenotes\b',
        'suggests',
        text,
        flags=re.IGNORECASE
    )
    
    # Rule 6: Standardize "foretells" -> "suggests"
    text = re.sub(
        r'\bforetells\s+that\b',
        'suggests that',
        text,
        flags=re.IGNORECASE
    )
    text = re.sub(
        r'\bforetells\b',
        'suggests',
        text,
        flags=re.IGNORECASE
    )
    
    # Rule 7: Standardize "portends" -> "suggests"
    text = re.sub(
        r'\bportends\s+that\b',
        'suggests that',
        text,
        flags=re.IGNORECASE
    )
    text = re.sub(
        r'\bportends\b',
        'suggests',
        text,
        flags=re.IGNORECASE
    )
    
    # Rule 8: Standardize "augurs" -> "suggests"
    text = re.sub(
        r'\baugurs\s+(ill|well)\s+for\b',
        r'suggests \1 outcomes for',
        text,
        flags=re.IGNORECASE
    )
    text = re.sub(
        r'\baugurs\b',
        'suggests',
        text,
        flags=re.IGNORECASE
    )
    
    # Rule 9: Standardize "indicates" -> "suggests" (optional, but for consistency)
    # Actually, let's keep "indicates" as it's fine
    
    # Rule 10: Clean up extra spaces
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Capitalize first letter
    if text:
        text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
    
    return text

def create_normalized_short(explanations: List[str], max_sentences: int = 2) -> str:
    """
    Create a short version (1-2 sentences) from normalized explanations.
    Takes the first 1-2 sentences from the first explanation, or combines themes.
    """
    if not explanations:
        return ""
    
    # Take first explanation and extract first 1-2 sentences
    first_explanation = explanations[0]
    
    # Split by sentence endings
    sentences = re.split(r'[.!?]+', first_explanation)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Take first max_sentences sentences
    selected = sentences[:max_sentences]
    result = '. '.join(selected)
    
    # Add period if not ending with punctuation
    if result and not result[-1] in '.!?':
        result += '.'
    
    return result

def process_dream_database():
    """
    Process the dream database to add normalized fields.
    """
    print("Loading dream database...")
    with open(DREAM_DB_FILE, "r", encoding="utf-8") as f:
        dream_db = json.load(f)
    
    print(f"Processing {len(dream_db)} entries...")
    
    # Unlock file for writing
    os.chmod(DREAM_DB_FILE, 0o644)
    
    try:
        for i, entry in enumerate(dream_db):
            word = entry.get("word", "")
            explanations = entry.get("explanations", [])
            
            if not explanations:
                print(f"  [{i+1}/{len(dream_db)}] {word}: No explanations, skipping normalization")
                continue
            
            # Normalize each explanation
            normalized = []
            for exp in explanations:
                normalized_exp = normalize_explanation(exp, word)
                if normalized_exp:
                    normalized.append(normalized_exp)
            
            # Add normalized field
            entry["normalized"] = normalized
            
            # Create short version (1-2 sentences) if there are many explanations
            if len(explanations) > 3:
                normalized_short = create_normalized_short(normalized, max_sentences=2)
                if normalized_short:
                    entry["normalized_short"] = normalized_short
            
            if (i + 1) % 100 == 0:
                print(f"  Processed {i+1}/{len(dream_db)} entries...")
        
        # Write back to file
        print("Writing normalized database...")
        with open(DREAM_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(dream_db, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully normalized {len(dream_db)} entries!")
        print(f"  - Added 'normalized' field to all entries")
        print(f"  - Added 'normalized_short' field to entries with >3 explanations")
        
    finally:
        # Lock file back to read-only
        os.chmod(DREAM_DB_FILE, 0o444)
        print("Database locked (read-only).")

if __name__ == "__main__":
    process_dream_database()
