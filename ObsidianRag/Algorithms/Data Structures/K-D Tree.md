---
category: Spatial & Dynamic Trees
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:32:02.556432+00:00
generated_by: claude
auto_generated: true
---

# K-D Tree

**Parent:** [[Data Structures MOC]] → Spatial & Dynamic Trees
**Tags:** #data-structures #kd-tree #spatial

## Definition
A binary tree that recursively partitions k-dimensional space by alternating the splitting axis at each depth, supporting nearest-neighbor and range queries over multi-dimensional points.

## Problem Recognition Signals
- "Given a set of 2D/3D points, answer nearest-neighbor or range (rectangle) queries" where a plain segment tree/BIT (one-dimensional) doesn't apply.
- Problems requiring dynamic insertion of multi-dimensional points combined with range or nearest queries (as opposed to a static offline sweep-line approach).

## Complexity
- Time: O(log n) average per query for balanced/static construction, degrading toward O(sqrt(n)) to O(n) under heavy insertion without rebalancing (often mitigated by periodic full rebuilds)
- Space: O(n)

## When to Use
- Multi-dimensional nearest-neighbor or range queries where sorting/sweeping in one dimension isn't sufficient, especially when queries are interleaved with insertions.

## Idea
At each tree level, split the current point set by the median along one coordinate axis (cycling axes by depth), recursing into left/right halves; range queries prune subtrees whose bounding region doesn't intersect the query region, and nearest-neighbor search prunes subtrees whose bounding region is farther than the current best found distance.

## Related
- [[Convex Hull (Monotone Chain)]]
- [[Sqrt Decomposition]]
