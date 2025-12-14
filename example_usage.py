#!/usr/bin/env python3
"""
Example usage of the Dream-Quote Matcher.
"""

from dream_quote_matcher import DreamQuoteMatcher

def main():
    # Initialize the matcher (loads databases)
    matcher = DreamQuoteMatcher()
    
    # Example: User inputs their dream
    user_dream = input("Enter your dream: ").strip()
    
    if not user_dream:
        print("No dream entered.")
        return
    
    # Match dream to symbols and quotes
    result = matcher.match(user_dream)
    
    # Display results
    print("\n" + "="*80)
    print("Dream Interpretation Results")
    print("="*80)
    
    if not result["symbols"]:
        print("\nNo matching symbols found in your dream.")
        print("Try using more specific words from common dream symbols.")
        return
    
    for i, symbol_result in enumerate(result["symbols"], 1):
        print(f"\n[{i}] Symbol: {symbol_result['word']}")
        print(f"\nExplanation:")
        print(f"  {symbol_result['explanation']}")
        
        if symbol_result['quote']:
            quote = symbol_result['quote']
            print(f"\nRelated Quote:")
            print(f"  \"{quote['quote']}\"")
            print(f"  - {quote['author']}")
        else:
            print("\nNo matching quote found.")
        
        print("-" * 80)

if __name__ == "__main__":
    main()
