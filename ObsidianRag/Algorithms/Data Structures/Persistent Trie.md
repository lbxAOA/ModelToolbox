---
category: Persistent Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:32:02.556432+00:00
generated_by: claude
auto_generated: true
---

# Persistent Trie

**Parent:** [[Data Structures MOC]] → Persistent Structures
**Tags:** #data-structures #persistent-trie #trie

## Definition
A binary (or general) trie where each insertion creates a new version via path-copying (as in a persistent segment tree), commonly used as a binary trie over bits to answer "maximum XOR with an element from version k's prefix" queries.

## Problem Recognition Signals
- "Given a prefix-sum-like array (e.g. XOR-prefix), answer 'max XOR of x with an element in range/version [l, r]'" — the classic persistent-XOR-trie signature.

## Complexity
- Time: O(log(max value)) per insertion (new version) or query
- Space: O(n log(max value)) total across all versions

## When to Use
- Range/historical maximum-XOR queries where a plain (non-persistent) trie can only answer queries against the full/current set, not an arbitrary prefix/range of insertions.

## Idea
Same path-copying idea as a persistent segment tree, applied to a binary trie over bit representations: each insertion copies only the O(log(max value)) nodes along the new number's bit path, sharing the rest with the previous version.

## Related
- [[Trie]]
- [[Persistent Segment Tree]]
- [[Linear (XOR) Basis]]
