#!/usr/bin/env python3
"""
Filter quotes database to only clean quotes in the format:
Quote text
    - Author
"""

import json
import re
from pathlib import Path

INPUT_FILE = Path("data/quotes_database.json")
OUTPUT_FILE = Path("data/quotes_clean.txt")

def is_clean_quote(quote_text, author):
    """Check if a quote is clean and suitable for output."""
    # Must have an author (not Unknown)
    if not author or author == "Unknown":
        return False
    
    # Must have minimum length
    if len(quote_text) < 20:
        return False
    
    # Filter out quotes that start with "..." (fragments)
    if quote_text.strip().startswith('...'):
        return False
    
    # Filter out quotes with angle brackets (stage directions)
    if '<' in quote_text and '>' in quote_text:
        return False
    
    # Filter out quotes that start with brackets (stage directions)
    if quote_text.strip().startswith('['):
        return False
    
    # Must have at least some letters (not just symbols/numbers)
    if not re.search(r'[a-zA-Z]{4,}', quote_text):
        return False
    
    # Filter out code/technical content
    code_indicators = ['/*', '*/', '//', 'function', 'return', 'void', 'int ', 'char ', 
                      'include', '#define', 'if (', 'else', 'while (', 'for (', 
                      'kernel', 'error_code', 'i386', 'sparc', 'linux', 'unix',
                      'integral', 'cos(', 'sin(', 'log(', 'sqrt', 'dz', 'pi/']
    quote_lower = quote_text.lower()
    if any(indicator in quote_lower for indicator in code_indicators):
        return False
    
    # Check for too many special characters (likely formulas/ASCII art)
    special_chars = len(re.findall(r'[^\w\s\.,!?;:\'\"-]', quote_text))
    total_chars = len(quote_text.replace(' ', ''))
    if total_chars > 0 and special_chars / total_chars > 0.15:
        return False
    
    # Must look like natural language (have common words)
    common_words = ['the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'be', 
                   'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 
                   'would', 'could', 'should', 'may', 'might', 'can', 'this', 
                   'that', 'with', 'from', 'for', 'about', 'into', 'through',
                   'who', 'what', 'when', 'where', 'why', 'how']
    if not any(word in quote_lower for word in common_words):
        return False
    
    # Filter out quotes that look like math formulas
    if re.search(r'\d+\s*[+\-*/=]\s*\d+', quote_text):
        return False
    
    # Filter out quotes with too many numbers
    numbers = len(re.findall(r'\d+', quote_text))
    if numbers > 3:
        return False
    
    # Must start with a capital letter or quote mark (complete thought)
    first_char = quote_text.strip()[0] if quote_text.strip() else ''
    if first_char and first_char not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ"':
        return False
    
    return True

def format_quote(quote_text, author):
    """Format quote in the requested format."""
    # Clean up quote text - preserve line breaks if they exist naturally
    # But normalize excessive whitespace
    quote_text = re.sub(r'\s+', ' ', quote_text.strip())
    
    # Split into lines if quote is long (for better readability)
    # Keep it as one line for now, but we can wrap if needed
    lines = []
    words = quote_text.split()
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > 80 and current_line:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            current_line.append(word)
            current_length += len(word) + 1
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Format: quote lines, then author with indentation
    formatted = '\n'.join(lines)
    formatted += f'\n    - {author}'
    
    return formatted

def main():
    print("Filtering quotes database...")
    
    # Load the quotes database
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    quotes = data.get('quotes', [])
    print(f"Total quotes in database: {len(quotes)}")
    
    # Filter clean quotes
    clean_quotes = []
    for quote_data in quotes:
        quote_text = quote_data.get('quote', '')
        author = quote_data.get('author', '')
        
        if is_clean_quote(quote_text, author):
            clean_quotes.append((quote_text, author))
    
    print(f"Clean quotes found: {len(clean_quotes)}")
    
    # Format and write to file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for quote_text, author in clean_quotes:
            formatted = format_quote(quote_text, author)
            f.write(formatted)
            f.write('\n\n')
    
    print(f"Saved {len(clean_quotes)} clean quotes to {OUTPUT_FILE}")
    
    # Show some examples
    print("\nExamples:")
    for quote_text, author in clean_quotes[:5]:
        print(f"\n{format_quote(quote_text, author)}")

if __name__ == "__main__":
    main()
