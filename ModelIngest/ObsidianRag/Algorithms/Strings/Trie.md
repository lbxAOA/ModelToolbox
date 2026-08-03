---
category: Hashing & Automata
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:17:23.702564+00:00
generated_by: claude
auto_generated: true
---

# Trie

**Parent:** [[Strings MOC]] → Hashing & Automata
**Tags:** #strings #trie

## Definition
A tree where each edge represents one character, and each root-to-node path represents the prefix spelled out along it, allowing a set of strings to share common prefixes as shared paths.

## Problem Recognition Signals
- "Insert/search a dictionary of words and answer prefix queries" (autocomplete, prefix counting).
- XOR-related problems phrased as "maximize XOR of a value with an element from a set" (binary trie over bit representations).

## Complexity
- Time: O(L) per insert/search/query, for string length L
- Space: O(total characters across all inserted strings × alphabet size), reducible with compressed tries

## When to Use
- Storing a dictionary of strings with efficient prefix-based operations, or representing binary numbers to answer maximum-XOR-pair-style queries (a binary/bitwise trie).

## Idea
Each node has up to |alphabet| children; inserting a string walks/creates a path character by character from the root, marking the final node as a string end. Query operations (prefix count, exact match) walk the same path and inspect visited nodes' metadata.

## Related
- [[Aho-Corasick Automaton]]
- [[Linear (XOR) Basis]]
- [[Persistent Trie]]
