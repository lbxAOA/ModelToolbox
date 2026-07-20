---
category: Range Query Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:28:58.064828+00:00
generated_by: claude
auto_generated: true
---

# Segment Tree

**Parent:** [[Data Structures MOC]] → Range Query Structures
**Tags:** #data-structures #segment-tree

## Definition
A binary tree over array indices where each node represents a range and stores an aggregate (sum/min/max/etc.) of that range, supporting point updates and arbitrary range queries in O(log n).

## Problem Recognition Signals
- "Point update, range query" (or range update, range query with lazy propagation) for an operation Fenwick trees don't directly support (min/max, or requiring custom merge logic).
- Any problem needing O(log n) range aggregation with updates that isn't a pure prefix sum.

## Complexity
- Time: O(log n) per update/query, O(n) to build
- Space: O(n) (typically 4n array size or 2n with an iterative layout)

## When to Use
- Dynamic range queries/updates for operations beyond simple sums (min, max, gcd, custom monoid merges), or when range (not just point) updates are needed via lazy propagation.

## Idea
Each node covers range [l, r]; leaves are single elements, and internal nodes store the merge of their two children's aggregates. Point update walks down to the relevant leaf and recomputes aggregates back up; range query recursively combines the O(log n) maximal sub-ranges ("canonical nodes") that exactly cover the query range.

## Related
- [[Fenwick Tree]]
- [[Segment Tree with Lazy Propagation]]
- [[Sparse Table]]
