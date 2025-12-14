#!/usr/bin/env python3
"""
Extract dream topics and their explanations from Miller's book.
Creates a JSON database with word -> list of explanations.
"""

import json
import re
from pathlib import Path

BOOK_FILE = Path("../Title_Ten Thousand Dreams Interpreted.txt")
OUTPUT_FILE = Path("../data/dream_database.json")

def extract_dream_database():
    """Extract all dream topics and their explanations."""
    
    with open(BOOK_FILE, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Pattern to find dream topic entries: _Word_.
    topic_pattern = r'^_([A-Z][A-Za-z\s&,\-]+)_\.'
    
    # Find all topic matches
    topics = []
    matches = list(re.finditer(topic_pattern, content, re.MULTILINE))
    
    for i, match in enumerate(matches):
        topic_word = match.group(1).strip()
        start_pos = match.end()
        
        # Find the end position (next topic or end of file)
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(content)
        
        # Extract the text for this topic
        topic_text = content[start_pos:end_pos].strip()
        
        # Extract all explanations (sentences starting with "To")
        explanations = []
        
        # Split by lines and find "To" sentences
        lines = topic_text.split('\n')
        current_explanation = []
        
        for line in lines:
            line = line.strip()
            if not line:
                # Empty line - if we have accumulated text, save it
                if current_explanation:
                    explanations.append(' '.join(current_explanation))
                    current_explanation = []
                continue
            
            # Check if line starts with "To" (new explanation)
            if re.match(r'^To\s+', line, re.IGNORECASE):
                # Save previous explanation if exists
                if current_explanation:
                    explanations.append(' '.join(current_explanation))
                # Start new explanation
                current_explanation = [line]
            else:
                # Continuation of current explanation
                if current_explanation:
                    current_explanation.append(line)
                # If no current explanation but line exists, might be a continuation
                # from previous (rare case)
                elif line and not line.startswith('['):
                    # Some entries might not start with "To"
                    current_explanation = [line]
        
        # Don't forget the last explanation
        if current_explanation:
            explanations.append(' '.join(current_explanation))
        
        # Clean up explanations
        cleaned_explanations = []
        for exp in explanations:
            exp = re.sub(r'\s+', ' ', exp).strip()
            # Remove footnote markers like [10]
            exp = re.sub(r'\[\d+\]', '', exp)
            if exp and len(exp) > 10:  # Only keep meaningful explanations
                cleaned_explanations.append(exp)
        
        if cleaned_explanations:
            topics.append({
                "word": topic_word,
                "explanations": cleaned_explanations
            })
    
    return topics

def main():
    print("Extracting dream database from Miller's book...")
    
    topics = extract_dream_database()
    
    # Create output directory if needed
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    
    # Save to JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2, ensure_ascii=False)
    
    print(f"Extracted {len(topics)} dream topics")
    print(f"Saved to {OUTPUT_FILE}")
    
    # Show some examples
    print("\nExamples:")
    for topic in topics[:5]:
        print(f"\n{topic['word']}:")
        for i, exp in enumerate(topic['explanations'][:2], 1):
            print(f"  {i}. {exp[:80]}...")

if __name__ == "__main__":
    main()

