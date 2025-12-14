#!/usr/bin/env python3
"""
Fix corrupted dream database - clean up the last entry that has Project Gutenberg text.
"""

import json
import os
from pathlib import Path

DREAM_DB_FILE = Path("data/dream_database.json")

def fix_database():
    """Fix the corrupted last entry."""
    print("Loading dream database...")
    with open(DREAM_DB_FILE, "r", encoding="utf-8") as f:
        dream_db = json.load(f)
    
    print(f"Total entries: {len(dream_db)}")
    
    # Check last entry
    last_entry = dream_db[-1]
    print(f"Last entry: {last_entry['word']}")
    print(f"Explanations count: {len(last_entry.get('explanations', []))}")
    
    # Fix the last entry - keep only the first valid explanation
    if last_entry['word'] == "Zoological Garden":
        valid_explanation = "To dream of visiting zoological gardens, denotes that you will have a varied fortune. Sometimes it seems that enemies will overpower you and again you stand in the front rank of success. You will also gain knowledge by travel and sojourn in foreign countries."
        
        # Keep only the first valid explanation
        last_entry['explanations'] = [valid_explanation]
        
        # Update normalized if it exists
        if 'normalized' in last_entry:
            normalized_exp = valid_explanation.replace("denotes", "suggests")
            last_entry['normalized'] = [normalized_exp]
        
        # Update normalized_short
        if 'normalized_short' in last_entry:
            last_entry['normalized_short'] = normalized_exp if 'normalized_exp' in locals() else valid_explanation.replace("denotes", "suggests")
        
        print(f"Fixed last entry - now has {len(last_entry['explanations'])} explanation(s)")
    
    # Unlock file for writing
    os.chmod(DREAM_DB_FILE, 0o644)
    
    try:
        # Write back to file
        print("\nWriting fixed database...")
        with open(DREAM_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(dream_db, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully fixed database! Total entries: {len(dream_db)}")
        
    finally:
        # Lock file back to read-only
        os.chmod(DREAM_DB_FILE, 0o444)
        print("Database locked (read-only).")

if __name__ == "__main__":
    fix_database()
