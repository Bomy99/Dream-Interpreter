#!/usr/bin/env python3
"""Quick test of the matcher."""

from dream_quote_matcher import DreamQuoteMatcher

matcher = DreamQuoteMatcher()
result = matcher.match("I saw a snake in my dream")
print(f"Test successful! Found {len(result['symbols'])} symbols")
for s in result['symbols']:
    print(f"  - {s['word']}")
