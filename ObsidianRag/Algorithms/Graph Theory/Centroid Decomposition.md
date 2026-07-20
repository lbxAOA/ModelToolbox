---
category: Tree Algorithms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:39:12.857299+00:00
generated_by: claude
auto_generated: true
---

# Centroid Decomposition

**Parent:** [[Graph Theory MOC]] → Tree Algorithms
**Tags:** #graph-theory #centroid-decomposition #tree

## Definition
Recursively decomposes a tree by repeatedly removing its centroid (a node whose removal splits the tree into pieces each of size ≤ half the current tree), building a "centroid tree" of depth O(log n) that's useful for answering path-counting/aggregation queries.

## Problem Recognition Signals
- "Count pairs of nodes whose path satisfies some distance/sum condition" (e.g. "count paths of length exactly k", "count pairs at distance ≤ d") — the classic centroid-decomposition divide-and-conquer-on-trees signature.

## Complexity
- Time: O(n log n) to build the decomposition, typically O(n log n) or O(n log² n) total for path-counting queries processed through it
- Space: O(n log n) (each node appears in O(log n) centroid subtrees)

## When to Use
- Problems requiring aggregation/counting over all pairs of nodes' paths through varying centroids, using a divide-and-conquer-on-trees strategy.

## Idea
Find the centroid of the current tree (a node where every remaining subtree after removal has size ≤ n/2), process all paths passing through the centroid (usually via a per-subtree DFS collecting depth/distance info combined across subtrees), remove the centroid, and recurse independently into each remaining piece — recursion depth is O(log n) since each step at least halves the component size.

## Related
- [[Tree DP]]
- [[Divide and Conquer]]
