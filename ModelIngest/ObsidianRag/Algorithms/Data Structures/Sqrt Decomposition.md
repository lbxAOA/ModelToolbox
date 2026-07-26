---
category: Decomposition
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:32:02.556432+00:00
generated_by: claude
auto_generated: true
---

# Sqrt Decomposition

**Parent:** [[Data Structures MOC]] → Decomposition
**Tags:** #data-structures #sqrt-decomposition #block-decomposition

## Definition
Divides an array (or query sequence, e.g. in Mo's algorithm) into blocks of size roughly sqrt(n), precomputing an aggregate per block so range updates/queries touch O(sqrt(n)) full blocks plus O(sqrt(n)) individual boundary elements.

## Problem Recognition Signals
- Range update/range query problems where the operation doesn't fit a segment tree's lazy-propagation model cleanly (e.g. range update is a complex non-composable operation), but an O(sqrt(n)) per operation is fast enough.
- Any "decompose into blocks" phrasing, or as the underlying mechanism for Mo's algorithm and block-based string/array structures.

## Complexity
- Time: O(sqrt(n)) per update/query
- Space: O(n)

## When to Use
- The needed operation is awkward to express as a segment tree merge/lazy-tag but is simple to apply per-block-or-per-element, and O(sqrt(n)) per operation fits the time limit.

## Idea
Partition the array into ~sqrt(n) blocks of ~sqrt(n) elements, maintaining a per-block aggregate; a range operation spanning multiple blocks touches the (at most 2) partial boundary blocks element-by-element and the fully-covered blocks via their precomputed aggregate in O(1) each.

## Related
- [[Mo's Algorithm]]
- [[Segment Tree]]
