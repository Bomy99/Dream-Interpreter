#!/usr/bin/env python3
"""Verify the quotes database."""

import json

with open("../data/quotes_database.json", "r", encoding="utf-8") as f:
    d = json.load(f)

print(f"Total quotes: {d['stats']['total_quotes']}")
print(f"Total keywords: {d['stats']['total_keywords']}")
print(f"Quotes with author: {d['stats']['quotes_with_author']}")

print("\n=== Sample quotes with authors ===")
good_quotes = [q for q in d['quotes'] if q['author'] != 'Unknown' and len(q['quote']) > 50]
for i, q in enumerate(good_quotes[:5], 1):
    print(f"\n{i}. {q['quote'][:100]}...")
    print(f"   Author: {q['author']}")
    print(f"   Keywords: {', '.join(q['keywords'][:8])}")

print("\n=== Keyword index examples ===")
for keyword in ['dream', 'fear', 'love', 'desire', 'unconscious']:
    matches = d['keyword_index'].get(keyword, [])
    print(f"\n'{keyword}': {len(matches)} matches")
    if matches:
        for q in matches[:2]:
            print(f"  - {q['quote'][:70]}... ({q['author']})")

