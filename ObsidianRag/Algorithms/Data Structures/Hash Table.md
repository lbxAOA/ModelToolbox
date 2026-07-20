---
category: Linear Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:28:58.064828+00:00
generated_by: claude
auto_generated: true
---

# Hash Table

**Parent:** [[Data Structures MOC]] → Linear Structures
**Tags:** #data-structures #hash-table

## Definition
Maps keys to values using a hash function to compute an array index, giving average O(1) insert/lookup/delete, with collisions resolved via chaining or open addressing.

## Problem Recognition Signals
- "Count occurrences of / check membership of arbitrary (possibly large-range or non-integer) keys quickly."
- De-duplication, frequency counting, or memoization keyed on complex/composite values.

## Complexity
- Time: O(1) average for insert/lookup/delete, O(n) worst case (pathological collisions)
- Space: O(n)

## When to Use
- Fast average-case key-value association where keys don't fit a small dense integer range (ruling out plain array indexing).

## Idea
Compute hash(key) mod table_size to get a bucket index; store colliding keys in a chain (linked list) at that bucket, or probe subsequent slots (open addressing) until an empty one is found; resize and rehash when the load factor grows too high.

## Related
- [[String Hashing]]
- [[Trie]]
