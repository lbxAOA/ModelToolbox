---
category: Offline Techniques
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:45:57.835091+00:00
generated_by: claude
auto_generated: true
---

# Mo's Algorithm on Trees

**Parent:** [[Miscellaneous MOC]] → Offline Techniques
**Tags:** #miscellaneous #mos-algorithm #trees #offline

## Definition
Adapts Mo's algorithm to answer offline path queries on a tree, by flattening the tree into a linear sequence via an Euler tour (each node appearing twice) so a tree path corresponds to a contiguous range, then applying standard Mo's algorithm with a symmetric-difference "toggle" update rule.

## Problem Recognition Signals
- "q offline queries about the path between two nodes in a tree" (e.g. "count distinct values on the path from u to v") where segment-tree-based Heavy-Light Decomposition doesn't naturally support the query type (similar to why Mo's is used over segment trees on arrays).

## Complexity
- Time: O((n + q) √n)
- Space: O(n + q)

## When to Use
- Offline path queries on a static tree for query types that support incremental add/remove but not easy segment-tree merging.

## Idea
Produce an Euler tour where each node appears exactly twice (on entry and exit); a path between u and v (assuming neither is an ancestor of the other) corresponds to the tour range between u's and v's occurrences with each node inside toggled twice (cancelling out) except LCA-excluded nodes and the path endpoints; run standard Mo's algorithm over this tour with an "add/remove toggles a node's contribution" update rule, handling the LCA case specially.

## Related
- [[Mo's Algorithm]]
- [[Lowest Common Ancestor (Binary Lifting)]]
- [[Heavy-Light Decomposition]]
