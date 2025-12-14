#!/usr/bin/env python3
"""
Runtime dream-to-quote matching system.
Matches up to 2 words from user's dream to dream_database symbols,
chooses best explanation by token overlap, and selects quotes by keyword overlap.
All processing is deterministic and offline.
"""

import json
import re
from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple, Optional

DREAM_DB_FILE = Path("data/dream_database.json")
QUOTES_DB_FILE = Path("data/quotes_database.json")

class DreamQuoteMatcher:
    def __init__(self):
        """Initialize the matcher with loaded databases."""
        print("Loading dream database...")
        with open(DREAM_DB_FILE, "r", encoding="utf-8") as f:
            self.dream_db = json.load(f)
        
        print("Loading quotes database...")
        with open(QUOTES_DB_FILE, "r", encoding="utf-8") as f:
            quotes_data = json.load(f)
            self.quotes_db = quotes_data.get("quotes", [])
        
        # Create lookup structures for efficient matching
        self._build_indexes()
        print("Databases loaded and indexed.")
    
    def _build_indexes(self):
        """Build indexes for fast lookup."""
        # Create lowercase word -> dream entry mapping
        self.dream_word_map = {}
        for entry in self.dream_db:
            word = entry["word"]
            # Store both original case and lowercase
            self.dream_word_map[word.lower()] = entry
            self.dream_word_map[word] = entry
        
        # Create keyword -> quotes mapping for fast lookup
        self.keyword_to_quotes = {}
        for quote in self.quotes_db:
            for keyword in quote.get("keywords", []):
                keyword_lower = keyword.lower()
                if keyword_lower not in self.keyword_to_quotes:
                    self.keyword_to_quotes[keyword_lower] = []
                self.keyword_to_quotes[keyword_lower].append(quote)
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words (lowercase, alphanumeric only)."""
        # Extract words, convert to lowercase
        tokens = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        # Filter out very short words (1-2 chars) and common stopwords that shouldn't count as symbols
        stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'was', 'are', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'me', 'him', 'us', 'them'}
        # Only keep meaningful words (3+ chars) that aren't stopwords
        meaningful_tokens = [t for t in tokens if len(t) >= 3 and t not in stopwords]
        return meaningful_tokens
    
    def _calculate_token_overlap(self, text1: str, text2: str) -> float:
        """Calculate token overlap score between two texts."""
        tokens1 = set(self._tokenize(text1))
        tokens2 = set(self._tokenize(text2))
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1 & tokens2
        union = tokens1 | tokens2
        
        # Jaccard similarity
        if not union:
            return 0.0
        return len(intersection) / len(union)
    
    def _normalize_plural(self, word: str) -> str:
        """Normalize word to handle plurals - returns singular form."""
        word_lower = word.lower()
        
        # Skip if too short
        if len(word_lower) <= 2:
            return word_lower
        
        # Common plural endings
        if word_lower.endswith('ies') and len(word_lower) > 4:
            # cities -> city, flies -> fly
            return word_lower[:-3] + 'y'
        elif word_lower.endswith('es') and len(word_lower) > 4:
            # matches -> match, boxes -> box, buses -> bus
            if word_lower.endswith('ches') or word_lower.endswith('shes') or word_lower.endswith('xes') or word_lower.endswith('zes'):
                return word_lower[:-2]
            elif word_lower.endswith('ves') and not word_lower.endswith('aves'):  # Don't convert "saves" -> "saf"
                # leaves -> leaf, knives -> knife, but not "saves"
                if word_lower.endswith('lves'):
                    return word_lower[:-3] + 'f'  # leaves -> leaf
                elif word_lower.endswith('ives'):
                    return word_lower[:-3] + 'fe'  # knives -> knife
                else:
                    return word_lower[:-2]
            else:
                return word_lower[:-2]
        elif word_lower.endswith('s') and len(word_lower) > 3:
            # cars -> car, wasps -> wasp, but not "is", "as", "us"
            # Don't remove 's' from words that end in 'ss' (like "class", "glass")
            if not word_lower.endswith('ss'):
                return word_lower[:-1]
        
        return word_lower
    
    def _words_match(self, word1: str, word2: str) -> bool:
        """Check if two words match, handling plurals and stems."""
        w1 = word1.lower()
        w2 = word2.lower()
        
        # Exact match
        if w1 == w2:
            return True
        
        # Normalize plurals
        w1_singular = self._normalize_plural(w1)
        w2_singular = self._normalize_plural(w2)
        
        # Check if normalized forms match
        if w1_singular == w2_singular:
            return True
        if w1 == w2_singular or w2 == w1_singular:
            return True
        
        # Check if one is a prefix of the other (for variations like "abandon" and "abandoned")
        min_len = min(len(w1_singular), len(w2_singular))
        if min_len >= 3:  # Only for words 3+ chars
            if w1_singular.startswith(w2_singular[:min_len-1]) or w2_singular.startswith(w1_singular[:min_len-1]):
                return True
        
        return False
    
    def _are_symbols_duplicates(self, symbol1: str, symbol2: str) -> bool:
        """Check if two symbols are variants/duplicates (e.g., 'Bed' and 'Bed Fellow', 'house' and 'housekeeper', 'fire' and 'firefighter')."""
        s1_lower = symbol1.lower().strip()
        s2_lower = symbol2.lower().strip()
        
        # Exact match
        if s1_lower == s2_lower:
            return True
        
        # Check if one word is contained in the other as a substring
        # Examples: "fire" in "firefighter", "house" in "housekeeper"
        # Use word boundaries to ensure we're matching whole words, not just substrings
        # Check if s1 (as a word) appears in s2
        if re.search(r'\b' + re.escape(s1_lower) + r'\b', s2_lower):
            return True
        # Check if s2 (as a word) appears in s1
        if re.search(r'\b' + re.escape(s2_lower) + r'\b', s1_lower):
            return True
        
        # Check if one symbol contains the other as a complete word
        # Examples: "Bed" in "Bed Fellow", "house" in "housekeeper"
        s1_words = s1_lower.split()
        s2_words = s2_lower.split()
        
        # If one is a single word and the other contains it as the first word
        if len(s1_words) == 1:
            first_word_s2 = s2_words[0] if s2_words else ""
            if s1_lower == first_word_s2:
                return True
            # Also check if s1 is a prefix of s2 (e.g., "house" in "housekeeper")
            if s2_lower.startswith(s1_lower):
                return True
        
        if len(s2_words) == 1:
            first_word_s1 = s1_words[0] if s1_words else ""
            if s2_lower == first_word_s1:
                return True
            # Also check if s2 is a prefix of s1 (e.g., "house" in "housekeeper")
            if s1_lower.startswith(s2_lower):
                return True
        
        # If one symbol's words are a subset of the other, they're duplicates
        s1_words_set = set(s1_words)
        s2_words_set = set(s2_words)
        if s1_words_set.issubset(s2_words_set) or s2_words_set.issubset(s1_words_set):
            return True
        
        # Check if they share the same first word (e.g., "Bed" and "Bed Fellow")
        if s1_words and s2_words:
            if s1_words[0] == s2_words[0]:
                return True
        
        return False
    
    def _find_dream_symbols(self, dream_text: str, max_symbols: int = 2, min_score: int = 200) -> List[Tuple[int, Dict, str]]:
        """
        Find up to max_symbols dream symbols from the dream text.
        STRICT MATCHING ONLY: Only matches symbols whose keyword appears as a whole word in user's text.
        - No fuzzy matching, no substring matching, no matching against explanation text
        - Only matches the symbol word/title itself
        - Allows plural/singular variations (e.g., "car" matches "cars")
        - For multi-word phrases, ALL words must appear as whole words
        Returns list of (score, entry, matched_token) tuples.
        """
        # Tokenize user's dream text - get set of actual words
        dream_tokens = self._tokenize(dream_text)
        dream_tokens_set = set(dream_tokens)
        # Create normalized set for plural/singular matching
        dream_tokens_normalized = {self._normalize_plural(t) for t in dream_tokens}
        
        # Find STRICT matches only - symbol word must appear as whole word in user text
        strict_matches = []
        for entry in self.dream_db:
            symbol_word = entry["word"].lower()
            symbol_word_normalized = self._normalize_plural(symbol_word)
            matched_token = None
            score = 0
            
            # Rule A: STRICT match - symbol word must appear as whole word in user's text
            # Check if it's a single word or multi-word phrase
            symbol_words = symbol_word.split()
            
            if len(symbol_words) == 1:
                # Single word symbol - must match exactly or as plural/singular
                if symbol_word in dream_tokens_set:
                    score = 1000 + len(symbol_word)
                    matched_token = symbol_word
                else:
                    # Check plural/singular variations (still whole word matching)
                    for token in dream_tokens:
                        token_normalized = self._normalize_plural(token)
                        # Exact match after normalization
                        if (token == symbol_word or 
                            token_normalized == symbol_word_normalized or
                            token == symbol_word_normalized or
                            token_normalized == symbol_word):
                            score = 950 + len(symbol_word)
                            matched_token = token
                            break
            else:
                # Multi-word phrase - ALL words must appear as whole words
                # Filter out stopwords from symbol phrase
                stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
                meaningful_symbol_words = [sw.lower() for sw in symbol_words if len(sw) >= 3 and sw.lower() not in stopwords]
                
                if len(meaningful_symbol_words) > 0:
                    # ALL meaningful words must appear as whole words in user's text
                    matched_tokens = []
                    all_matched = True
                    
                    for sw in meaningful_symbol_words:
                        sw_normalized = self._normalize_plural(sw)
                        found = False
                        
                        # Check exact match first
                        if sw in dream_tokens_set:
                            matched_tokens.append(sw)
                            found = True
                        else:
                            # Check normalized (plural/singular) match
                            for token in dream_tokens:
                                token_normalized = self._normalize_plural(token)
                                if sw_normalized == token_normalized or sw == token_normalized or sw_normalized == token:
                                    matched_tokens.append(token)
                                    found = True
                                    break
                        
                        if not found:
                            all_matched = False
                            break
                    
                    # Only score if ALL meaningful words were matched as whole words
                    if all_matched and len(matched_tokens) == len(meaningful_symbol_words):
                        score = 500 + len(symbol_word)
                        matched_token = " ".join(matched_tokens)
            
            # Only include if we have a strict match (score > 0 and matched_token)
            if score > 0 and matched_token:
                strict_matches.append((score, entry, matched_token))
        
        # Sort by score (descending), then by word length (longer first)
        strict_matches.sort(key=lambda x: (-x[0], -len(x[1]["word"])))
        
        # Remove duplicates/variants - keep the highest scoring one
        filtered_symbols = []
        for score, entry, matched_token in strict_matches:
            is_duplicate = False
            for i, (existing_score, existing_entry, existing_token) in enumerate(filtered_symbols):
                if self._are_symbols_duplicates(entry["word"], existing_entry["word"]):
                    is_duplicate = True
                    # Keep the one with higher score
                    if score > existing_score:
                        filtered_symbols[i] = (score, entry, matched_token)
                    break
            
            if not is_duplicate:
                filtered_symbols.append((score, entry, matched_token))
            
            # Stop if we have enough non-duplicate symbols
            if len(filtered_symbols) >= max_symbols:
                break
        
        return filtered_symbols
    
    def _choose_best_explanation(self, symbol: Dict, dream_text: str) -> str:
        """Choose the best explanation for a symbol based on token overlap with dream."""
        explanations = symbol.get("explanations", [])
        if not explanations:
            return ""
        
        # Calculate overlap score for each explanation
        scored_explanations = []
        for exp in explanations:
            score = self._calculate_token_overlap(dream_text, exp)
            scored_explanations.append((score, exp))
        
        # Sort by score (descending), then by length (shorter first for tie-breaking)
        scored_explanations.sort(key=lambda x: (-x[0], len(x[1])))
        
        return scored_explanations[0][1] if scored_explanations else explanations[0]
    
    def _quote_contains_symbol(self, quote: Dict, symbol_word: str) -> bool:
        """Check if quote text contains the symbol word."""
        quote_text = quote.get("quote", "").lower()
        symbol_lower = symbol_word.lower()
        # Check for exact word match (word boundaries)
        return bool(re.search(r'\b' + re.escape(symbol_lower) + r'\b', quote_text))
    
    def _calculate_keyword_overlap(self, quote: Dict, symbol_word: str) -> float:
        """Calculate keyword overlap score between quote and symbol."""
        quote_keywords = [k.lower() for k in quote.get("keywords", [])]
        symbol_lower = symbol_word.lower()
        
        # Bonus if symbol word is in quote keywords
        if symbol_lower in quote_keywords:
            return 1.0
        
        # Check if symbol word appears in quote text
        if self._quote_contains_symbol(quote, symbol_word):
            return 0.8
        
        # Check if any keyword is similar to symbol word
        for keyword in quote_keywords:
            if symbol_lower in keyword or keyword in symbol_lower:
                return 0.6
        
        # No overlap
        return 0.0
    
    def _get_symbol_keywords(self, symbol_word: str) -> List[str]:
        """Extract keywords from symbol word for matching."""
        # Split symbol into words and use first 2 as keywords
        words = symbol_word.lower().split()
        if len(words) >= 2:
            return [words[0], words[1]]
        elif len(words) == 1:
            # For single word, use it as the only keyword (will match "one keyword" case)
            return [words[0]]
        return []
    
    def _quote_matches_keywords(self, quote: Dict, keywords: List[str]) -> Tuple[bool, bool, int]:
        """
        Check if quote matches keywords.
        Returns: (matches_both, matches_one, match_count)
        """
        quote_keywords = [k.lower() for k in quote.get("keywords", [])]
        quote_keywords_set = set(quote_keywords)
        
        keyword1 = keywords[0].lower() if len(keywords) > 0 else ""
        keyword2 = keywords[1].lower() if len(keywords) > 1 else None
        
        matches = []
        if keyword1 and keyword1 in quote_keywords_set:
            matches.append(keyword1)
        if keyword2 and keyword2 in quote_keywords_set and keyword2 not in matches:
            matches.append(keyword2)
        
        match_count = len(matches)
        # For single keyword symbols, "matches_both" is always False
        matches_both = match_count >= 2 if keyword2 else False
        matches_one = match_count >= 1
        
        return matches_both, matches_one, match_count
    
    def _choose_best_quote(self, symbol: Dict, dream_text: str) -> Optional[Dict]:
        """
        Choose the best quote for a symbol based on keyword matching.
        Prefers quotes matching BOTH keywords, then ONE keyword.
        Always returns deterministically.
        """
        symbol_word = symbol["word"]
        symbol_keywords = self._get_symbol_keywords(symbol_word)
        
        if not symbol_keywords:
            return None
        
        # Separate quotes into categories
        quotes_both = []  # Quotes matching both keywords
        quotes_one = []   # Quotes matching one keyword
        quotes_none = []  # Quotes matching neither (fallback)
        
        for quote in self.quotes_db:
            matches_both, matches_one, match_count = self._quote_matches_keywords(quote, symbol_keywords)
            
            if matches_both:
                quotes_both.append((match_count, quote))
            elif matches_one:
                quotes_one.append((match_count, quote))
            else:
                # Check if symbol word appears in quote text as fallback
                if self._quote_contains_symbol(quote, symbol_word):
                    quotes_none.append((0, quote))
        
        # Prefer quotes matching both keywords
        if quotes_both:
            candidate_quotes = quotes_both
        elif quotes_one:
            candidate_quotes = quotes_one
        else:
            candidate_quotes = quotes_none if quotes_none else [(0, q) for q in self.quotes_db]
        
        # Score each candidate quote for deterministic selection
        scored_quotes = []
        for match_count, quote in candidate_quotes:
            # Calculate additional scores for tie-breaking
            keyword_score = match_count * 10  # Higher for more keyword matches
            
            # Check if symbol word appears in quote text
            text_match = 5 if self._quote_contains_symbol(quote, symbol_word) else 0
            
            # Token overlap with dream text (smaller weight)
            dream_overlap = self._calculate_token_overlap(dream_text, quote.get("quote", "")) * 2
            
            # Combined score
            combined_score = keyword_score + text_match + dream_overlap
            
            scored_quotes.append((combined_score, match_count, quote))
        
        # Sort deterministically: by combined score, then match count, then quote text
        scored_quotes.sort(key=lambda x: (-x[0], -x[1], x[2].get("quote", "")))
        
        return scored_quotes[0][2] if scored_quotes else None
    
    def match(self, dream_text: str) -> Dict:
        """
        Match dream text to symbols and quotes.
        
        Returns:
            {
                "symbols": [
                    {
                        "word": "Symbol",
                        "explanation": "Best explanation text",
                        "quote": {quote object}
                    }
                ],
                "message": "Optional message for user guidance",
                "show_freud_only": bool  # If True, show only Freud section
            }
        """
        # Find matching symbols with minimum score threshold
        matched_symbols_with_scores = self._find_dream_symbols(dream_text, max_symbols=10, min_score=200)
        
        # Filter out duplicates and ensure each symbol uses a UNIQUE word from user's input
        # Track which tokens from user's input have been used
        used_tokens = set()
        filtered_symbols = []
        
        for score, entry, matched_token in matched_symbols_with_scores:
            # Check if this symbol is a duplicate of an existing one
            is_duplicate = False
            for existing_entry in filtered_symbols:
                if self._are_symbols_duplicates(entry["word"], existing_entry["word"]):
                    is_duplicate = True
                    break
            
            if is_duplicate:
                continue
            
            # Check if the matched token(s) have already been used
            # For phrase matches, check all tokens in the phrase
            matched_tokens_list = matched_token.split() if matched_token else []
            token_already_used = False
            
            # Normalize tokens for comparison
            matched_tokens_normalized = {self._normalize_plural(t) for t in matched_tokens_list}
            used_tokens_normalized = {self._normalize_plural(t) for t in used_tokens}
            
            # Check if any matched token overlaps with already used tokens
            if matched_tokens_normalized & used_tokens_normalized:
                token_already_used = True
            
            if not token_already_used:
                # Mark these tokens as used
                for token in matched_tokens_list:
                    used_tokens.add(token.lower())
                filtered_symbols.append(entry)
            
            # Stop once we have enough non-duplicate symbols with unique tokens
            if len(filtered_symbols) >= 10:
                break
        
        # REQUIRE exactly 2 matches - if not, show Freud asking for more details
        results = []
        message = None
        show_freud_only = False
        
        if len(filtered_symbols) < 2:
            # Less than 2 symbols found - show only Freud with guidance message
            show_freud_only = True
            message = "Please add more details about your dream. What else did you see or feel?"
            
            # Still include the symbol(s) for Dream Yield display if any found
            for symbol in filtered_symbols:
                best_explanation = self._choose_best_explanation(symbol, dream_text)
                best_quote = self._choose_best_quote(symbol, dream_text)
                
                # Get book and emoji from symbol entry
                book = symbol.get("book")
                emoji = symbol.get("emoji")
                
                results.append({
                    "word": symbol["word"],
                    "explanation": best_explanation,
                    "quote": best_quote,
                    "book": book,
                    "emoji": emoji
                })
        else:
            # Exactly 2 or more symbols found - use the first 2 non-duplicate ones
            selected_symbols = filtered_symbols[:2]
            
            # Two symbols found - normal interpretation
            for symbol in selected_symbols:
                best_explanation = self._choose_best_explanation(symbol, dream_text)
                best_quote = self._choose_best_quote(symbol, dream_text)
                
                # Get book and emoji from symbol entry
                book = symbol.get("book")
                emoji = symbol.get("emoji")
                
                results.append({
                    "word": symbol["word"],
                    "explanation": best_explanation,
                    "quote": best_quote,
                    "book": book,
                    "emoji": emoji
                })
        
        return {
            "symbols": results,
            "message": message,
            "show_freud_only": show_freud_only
        }


def main():
    """Test the matcher with example dreams."""
    matcher = DreamQuoteMatcher()
    
    # Example dreams
    test_dreams = [
        "I dreamed about a dragon flying over a castle",
        "I saw a baby crying in my dream",
        "I was abandoned by my friends in the dream"
    ]
    
    print("\n" + "="*80)
    print("Testing Dream-Quote Matcher")
    print("="*80)
    
    for dream in test_dreams:
        print(f"\nDream: {dream}")
        print("-" * 80)
        result = matcher.match(dream)
        
        for symbol_result in result["symbols"]:
            print(f"\nSymbol: {symbol_result['word']}")
            print(f"Explanation: {symbol_result['explanation'][:100]}...")
            if symbol_result['quote']:
                quote = symbol_result['quote']
                print(f"Quote: {quote['quote'][:80]}...")
                print(f"Author: {quote['author']}")
                print(f"Keywords: {quote['keywords']}")
            print()


if __name__ == "__main__":
    main()
