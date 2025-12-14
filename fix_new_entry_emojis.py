#!/usr/bin/env python3
"""
Fix emoji assignments for newly added entries that should match their word names.
"""

import json
import os
from pathlib import Path

DREAM_DB_FILE = Path("data/dream_database.json")
EMOJIS_DIR = Path("without background")

# Words that should match emoji names directly
WORD_TO_EMOJI_MAP = {
    "Fear": "Nervous.png",  # Fear -> Nervous (closest available)
    "Fears": "Nervous.png",
    "Anxiety": "Nervous.png",
    "Helplessness": "Sad.png",
    "Pressure": "Sweat.png",
    "Shame": "Blush.png",
    "Desire": "Want.png",
    "Temptation": "Devil.png",
    "Guilt": "Hurt.png",
    "Liberation": "Cool.png",
    "Control": "Cool.png",
    "Loss of Control": "Nervous.png",  # Loss of control -> Nervous
    "Confidence": "Proud.png",
    "Confusion": "Question.png",
    "Anticipation": "Surprised.png",
    "Vulnerability": "Hurt.png",
    "Urgency": "Sweat.png",
    "Being Chased": "Nervous.png",  # Being chased -> Nervous
    "Being Tested": "Sweat.png",
    "Being Late": "Sweat.png",
    "Falling": "Nervous.png",  # Falling -> Nervous
    "Flying": "Cool.png",
    "Losing Teeth": "Nervous.png",  # Losing teeth -> Nervous
    "Being Attacked": "Hurt.png",
    "Being Unable to Move": "Nervous.png",  # Unable to move -> Nervous
    "Being Watched": "Nervous.png",
    "Being Trapped": "Nervous.png",  # Trapped -> Nervous
    "Lucid Dreaming": "Cool.png",
    "Nightmares": "Nervous.png",  # Nightmares -> Nervous
    "Recurring Dreams": "Question.png",
    "Sleep Paralysis": "Nervous.png",  # Sleep paralysis -> Nervous
    "Out-of-Body Experience": "Cool.png",
    "Astral Projection": "Cool.png",
    "Snake": "Devil.png",
    "Circle": "Cool.png",
    "Wheel": "Cool.png",
    "Phoenix": "Cool.png",
    "Tree": "Cool.png",
    "Yin and Yang": "Cool.png"
}

def fix_emojis():
    """Fix emoji assignments for new entries."""
    print("Loading dream database...")
    with open(DREAM_DB_FILE, "r", encoding="utf-8") as f:
        dream_db = json.load(f)
    
    # Get available emojis
    emojis_dir = EMOJIS_DIR
    available_emojis = {f.name.lower(): f.name for f in emojis_dir.glob("*.png")} if emojis_dir.exists() else {}
    
    print(f"Found {len(available_emojis)} emoji images")
    
    # Unlock file for writing
    os.chmod(DREAM_DB_FILE, 0o644)
    
    try:
        updated_count = 0
        
        for entry in dream_db:
            word = entry["word"]
            
            # Check if this word should have a specific emoji
            if word in WORD_TO_EMOJI_MAP:
                target_emoji = WORD_TO_EMOJI_MAP[word]
                
                # Verify emoji exists
                if target_emoji.lower() in available_emojis:
                    actual_emoji = available_emojis[target_emoji.lower()]
                    if entry.get("emoji") != actual_emoji:
                        entry["emoji"] = actual_emoji
                        updated_count += 1
                        print(f"  Updated '{word}': {entry.get('emoji', 'N/A')} -> {actual_emoji}")
        
        # Write back to file
        if updated_count > 0:
            print(f"\nWriting updated database...")
            with open(DREAM_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(dream_db, f, indent=2, ensure_ascii=False)
            
            print(f"Successfully updated {updated_count} entries with correct emojis!")
        else:
            print("No entries needed updating.")
        
    finally:
        # Lock file back to read-only
        os.chmod(DREAM_DB_FILE, 0o444)
        print("Database locked (read-only).")

if __name__ == "__main__":
    fix_emojis()
