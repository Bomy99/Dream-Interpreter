#!/usr/bin/env python3
"""
Extract quotes with authors and keywords from quote.txt.
Creates a JSON database where keywords map to quotes + authors.
This will be used to match words from dream explanations to relevant quotes.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

QUOTE_FILE = Path("../quote.txt")
OUTPUT_FILE = Path("../data/quotes_database.json")

def extract_keywords(text, min_length=4):
    """Extract meaningful keywords from text."""
    # Remove punctuation and convert to lowercase
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = text.split()
    
    # Filter out common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
        'every', 'some', 'any', 'no', 'not', 'only', 'just', 'more', 'most',
        'very', 'much', 'many', 'few', 'little', 'own', 'other', 'another',
        'such', 'than', 'then', 'there', 'here', 'where', 'when', 'why'
    }
    
    # Extract meaningful words
    keywords = []
    for word in words:
        word = word.strip()
        if len(word) >= min_length and word not in stop_words:
            keywords.append(word)
    
    return list(set(keywords))  # Remove duplicates

def is_ascii_art(text):
    """Check if text looks like ASCII art (too many special characters)."""
    if not text:
        return True
    
    # Count special characters
    special_chars = len(re.findall(r'[^\w\s]', text))
    total_chars = len(text.replace(' ', ''))
    
    if total_chars == 0:
        return True
    
    # If more than 30% special characters, likely ASCII art
    if special_chars / total_chars > 0.3:
        return True
    
    # Check for patterns common in ASCII art
    if re.search(r'[|\\/_\-=+*~`<>\[\]{}()]', text):
        special_pattern = len(re.findall(r'[|\\/_\-=+*~`<>\[\]{}()]', text))
        if special_pattern / total_chars > 0.2:
            return True
    
    return False

def parse_quote_block(block):
    """Parse a single quote block and extract quote, author, and keywords."""
    block = block.strip()
    if not block or len(block) < 20:  # Minimum length for meaningful quote
        return None
    
    # Skip ASCII art
    if is_ascii_art(block):
        return None
    
    # Look for author attribution (line starting with dash)
    lines = block.split('\n')
    quote_lines = []
    author = None
    author_info = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Check if this line starts with a dash (author attribution)
        if re.match(r'^\s*-\s+', line):
            # Extract author
            author_line = re.sub(r'^\s*-\s+', '', line)
            # Split author from additional info (dates, sources in parentheses)
            match = re.match(r'^([^(]+?)(?:\s*\(([^)]+)\))?\s*$', author_line)
            if match:
                author = match.group(1).strip()
                author_info = match.group(2) if match.group(2) else None
            else:
                author = author_line
            break
        else:
            quote_lines.append(line)
    
    if not quote_lines:
        return None
    
    quote_text = ' '.join(quote_lines).strip()
    
    # Clean up quote text
    quote_text = re.sub(r'\s+', ' ', quote_text)
    
    # Must have minimum length and look like actual text
    if len(quote_text) < 20:
        return None
    
    # Must have at least some letters (not just symbols/numbers)
    if not re.search(r'[a-zA-Z]{4,}', quote_text):
        return None
    
    # Filter out code/technical content
    code_indicators = ['/*', '*/', '//', 'function', 'return', 'void', 'int ', 'char ', 
                      'include', '#define', 'if (', 'else', 'while (', 'for (', 
                      'kernel', 'error_code', 'i386', 'sparc', 'linux', 'unix']
    if any(indicator in quote_text.lower() for indicator in code_indicators):
        return None
    
    # Must look like natural language (have common words)
    common_words = ['the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'be', 
                   'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 
                   'would', 'could', 'should', 'may', 'might', 'can', 'this', 
                   'that', 'with', 'from', 'for', 'about', 'into', 'through']
    quote_lower = quote_text.lower()
    if not any(word in quote_lower for word in common_words):
        return None
    
    # Extract keywords from quote
    keywords = extract_keywords(quote_text)
    
    # Need at least 3 meaningful keywords
    if len(keywords) < 3:
        return None
    
    return {
        "quote": quote_text,
        "author": author or "Unknown",
        "author_info": author_info,
        "keywords": keywords
    }

def create_keyword_index(quotes):
    """Create an index mapping keywords to quotes."""
    keyword_index = defaultdict(list)
    
    for quote_data in quotes:
        quote_id = len(keyword_index.get(quote_data['keywords'][0], []))
        for keyword in quote_data['keywords']:
            keyword_index[keyword].append({
                "quote": quote_data['quote'],
                "author": quote_data['author'],
                "author_info": quote_data.get('author_info'),
                "quote_id": quote_id
            })
    
    return dict(keyword_index)

def main():
    print("Extracting quotes database from quote.txt...")
    
    with open(QUOTE_FILE, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Split by % markers
    blocks = content.split('%')
    
    quotes = []
    for block in blocks:
        quote_data = parse_quote_block(block)
        if quote_data:
            quotes.append(quote_data)
    
    print(f"Extracted {len(quotes)} quotes")
    
    # Create keyword index
    keyword_index = create_keyword_index(quotes)
    
    print(f"Created index with {len(keyword_index)} unique keywords")
    
    # Create output structure
    output = {
        "quotes": quotes,
        "keyword_index": keyword_index,
        "stats": {
            "total_quotes": len(quotes),
            "total_keywords": len(keyword_index),
            "quotes_with_author": sum(1 for q in quotes if q['author'] != "Unknown")
        }
    }
    
    # Create output directory if needed
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    
    # Save to JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"Saved to {OUTPUT_FILE}")
    
    # Show some examples
    print("\nExamples:")
    for quote in quotes[:5]:
        print(f"\nQuote: {quote['quote'][:80]}...")
        print(f"Author: {quote['author']}")
        print(f"Keywords: {', '.join(quote['keywords'][:10])}")
    
    # Show keyword index example
    print("\n\nKeyword index example (keyword 'love'):")
    if 'love' in keyword_index:
        for item in keyword_index['love'][:3]:
            print(f"  - {item['quote'][:60]}... ({item['author']})")

if __name__ == "__main__":
    main()

