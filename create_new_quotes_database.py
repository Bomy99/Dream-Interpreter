#!/usr/bin/env python3
"""
Create a new quotes database from clean quotes file.
Format: quote ; Author ; ["keyword1","keyword2","keyword3","keyword4"]
"""

import json
import re
from pathlib import Path
from collections import Counter

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.tag import pos_tag
    NLTK_AVAILABLE = True
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        try:
            nltk.download('punkt_tab', quiet=True)
        except:
            try:
                nltk.download('punkt', quiet=True)
            except:
                pass
    try:
        nltk.data.find('taggers/averaged_perceptron_tagger')
    except LookupError:
        nltk.download('averaged_perceptron_tagger', quiet=True)
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
except (ImportError, Exception) as e:
    NLTK_AVAILABLE = False
    print(f"Warning: NLTK not available ({e}). Using fallback keyword extraction.")

INPUT_FILE = Path("data/quotes_clean.txt")
OUTPUT_FILE = Path("data/quotes_database.json")

# Stopwords and generic words to avoid
STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
    'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this',
    'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
    'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
    'every', 'some', 'any', 'no', 'not', 'only', 'just', 'more', 'most',
    'very', 'much', 'many', 'few', 'little', 'own', 'other', 'another',
    'such', 'than', 'then', 'there', 'here'
}

GENERIC_WORDS = {'dream', 'feel', 'something', 'person', 'life', 'thing', 'things',
                 'way', 'time', 'people', 'man', 'men', 'woman', 'women', 'one',
                 'ones', 'kind', 'kinds', 'sort', 'sorts', 'type', 'types'}

# POS tags: NN = noun, NNS = plural noun, NNP = proper noun, NNPS = plural proper noun
# VB = verb, VBD = past tense verb, VBG = gerund, VBN = past participle, VBP = present verb, VBZ = 3rd person verb
NOUN_TAGS = {'NN', 'NNS', 'NNP', 'NNPS'}
VERB_TAGS = {'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'}

def extract_keywords_nltk(text):
    """Extract 4 keywords using NLTK POS tagging."""
    # Tokenize and tag
    tokens = word_tokenize(text.lower())
    tagged = pos_tag(tokens)
    
    # Collect nouns and verbs
    nouns = []
    verbs = []
    
    for word, tag in tagged:
        # Skip stopwords, generic words, and short words
        if word in STOPWORDS or word in GENERIC_WORDS:
            continue
        if len(word) < 3:
            continue
        # Remove punctuation-only tokens
        if not re.search(r'[a-zA-Z]', word):
            continue
        
        # Clean word (remove punctuation)
        clean_word = re.sub(r'[^\w]', '', word)
        if len(clean_word) < 3:
            continue
        
        if tag in NOUN_TAGS:
            nouns.append(clean_word)
        elif tag in VERB_TAGS:
            verbs.append(clean_word)
    
    # Prefer concrete nouns
    keywords = []
    noun_counts = Counter(nouns)
    verb_counts = Counter(verbs)
    
    # Get top nouns (up to 4)
    top_nouns = [word for word, _ in noun_counts.most_common(4)]
    keywords.extend(top_nouns)
    
    # If we need more, add verbs
    if len(keywords) < 4 and verbs:
        remaining = 4 - len(keywords)
        top_verbs = [word for word, _ in verb_counts.most_common(remaining)]
        for verb in top_verbs:
            if verb not in keywords:
                keywords.append(verb)
    
    # If still need more, use any meaningful words
    if len(keywords) < 4:
        all_words = [re.sub(r'[^\w]', '', word.lower()) for word in tokens 
                    if word.lower() not in STOPWORDS and word.lower() not in GENERIC_WORDS
                    and len(re.sub(r'[^\w]', '', word)) >= 3]
        word_counts = Counter(all_words)
        for word, _ in word_counts.most_common(4):
            if word not in keywords:
                keywords.append(word)
                if len(keywords) >= 4:
                    break
    
    # Ensure exactly 4 keywords
    while len(keywords) < 4:
        keywords.append(keywords[-1] if keywords else "unknown")
    
    return keywords[:4]

def extract_keywords_fallback(text):
    """Fallback keyword extraction without NLTK using heuristics."""
    # Simple word frequency approach
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Filter stopwords and generic words
    filtered = [w for w in words if w not in STOPWORDS and w not in GENERIC_WORDS]
    
    if not filtered:
        return ["unknown", "unknown", "unknown", "unknown"]
    
    # Heuristic: words ending in common noun suffixes are likely nouns
    # Common noun endings: -tion, -sion, -ness, -ment, -ity, -er, -or, -ist, -ism
    noun_suffixes = ['tion', 'sion', 'ness', 'ment', 'ity', 'er', 'or', 'ist', 'ism', 'ing']
    
    # Separate potential nouns from other words
    potential_nouns = []
    other_words = []
    
    for word in filtered:
        is_noun = any(word.endswith(suffix) for suffix in noun_suffixes)
        # Also check if word appears after articles (the, a, an) - heuristic
        if is_noun or len(word) > 5:  # Longer words are often nouns
            potential_nouns.append(word)
        else:
            other_words.append(word)
    
    keywords = []
    
    # Get top nouns (up to 4)
    if potential_nouns:
        noun_counts = Counter(potential_nouns)
        top_nouns = [word for word, _ in noun_counts.most_common(4)]
        keywords.extend(top_nouns)
    
    # Add other words if needed
    if len(keywords) < 4 and other_words:
        remaining = 4 - len(keywords)
        other_counts = Counter(other_words)
        top_others = [word for word, _ in other_counts.most_common(remaining)]
        for word in top_others:
            if word not in keywords:
                keywords.append(word)
    
    # If still need more, use all filtered words
    if len(keywords) < 4:
        word_counts = Counter(filtered)
        for word, _ in word_counts.most_common(4):
            if word not in keywords:
                keywords.append(word)
                if len(keywords) >= 4:
                    break
    
    # Ensure exactly 4 keywords
    while len(keywords) < 4:
        keywords.append(keywords[-1] if keywords else "unknown")
    
    return keywords[:4]

def parse_clean_quotes_file(file_path):
    """Parse the clean quotes file and extract quotes with authors."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    quotes = []
    
    # Split by double newlines to get quote blocks
    blocks = content.split('\n\n')
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        lines = block.split('\n')
        quote_lines = []
        author = None
        
        for line in lines:
            # Check if this line is the author (starts with 4 spaces and dash)
            if re.match(r'^\s{4}-\s+', line):
                author = re.sub(r'^\s{4}-\s+', '', line).strip()
                break
            else:
                # This is part of the quote
                quote_lines.append(line.strip())
        
        if quote_lines and author:
            quote_text = ' '.join(quote_lines).strip()
            if quote_text:
                quotes.append((quote_text, author))
    
    return quotes

def main():
    print("Creating new quotes database from clean quotes file...")
    
    # Parse clean quotes file
    quotes = parse_clean_quotes_file(INPUT_FILE)
    print(f"Parsed {len(quotes)} quotes from {INPUT_FILE}")
    
    # Extract keywords for each quote
    database_entries = []
    use_nltk = NLTK_AVAILABLE
    extract_func = extract_keywords_nltk if use_nltk else extract_keywords_fallback
    
    print(f"Extracting keywords using {'NLTK' if use_nltk else 'fallback'} method...")
    for i, (quote_text, author) in enumerate(quotes):
        if (i + 1) % 1000 == 0:
            print(f"  Processed {i + 1}/{len(quotes)} quotes...")
        
        # Try NLTK, fall back if it fails
        if use_nltk:
            try:
                keywords = extract_keywords_nltk(quote_text)
            except Exception as e:
                if i == 0:  # Only print warning once
                    print(f"  NLTK failed, switching to fallback method: {e}")
                use_nltk = False
                extract_func = extract_keywords_fallback
                keywords = extract_keywords_fallback(quote_text)
        else:
            keywords = extract_func(quote_text)
        
        # Ensure exactly 4 keywords
        if len(keywords) < 4:
            keywords.extend(["unknown"] * (4 - len(keywords)))
        keywords = keywords[:4]
        
        # Format: quote ; Author ; ["keyword1","keyword2"]
        entry = {
            "quote": quote_text,
            "author": author,
            "keywords": keywords
        }
        database_entries.append(entry)
    
    # Create output structure
    output = {
        "quotes": database_entries,
        "stats": {
            "total_quotes": len(database_entries)
        }
    }
    
    # Save to JSON
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(database_entries)} quotes to {OUTPUT_FILE}")
    
    # Show some examples
    print("\nExamples:")
    for entry in database_entries[:5]:
        print(f"\n{entry['quote'][:60]}...")
        print(f"  Author: {entry['author']}")
        print(f"  Keywords: {entry['keywords']}")

if __name__ == "__main__":
    main()
