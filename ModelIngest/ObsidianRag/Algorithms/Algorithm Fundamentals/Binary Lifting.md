---
category: Ranges & Search
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:03:53.991853+00:00
generated_by: claude
auto_generated: true
---

# Binary Lifting

**Parent:** [[Algorithm Fundamentals MOC]] → Ranges & Search
**Tags:** #algorithm-fundamentals #binary-lifting

## Definition
Precompute, for each node/state, jumps of length 2^k (its 2^k-th ancestor/successor) so any jump of arbitrary length can be composed from O(log n) precomputed jumps.

## Problem Recognition Signals
- "Find the k-th ancestor of a node" or "find the ancestor of node v at depth d" on a tree.
- "Each node points to exactly one other node (functional graph); where do you end up after k steps?" with k astronomically large.
- Tree problems mentioning Lowest Common Ancestor with many queries.

## Complexity
- Time: O(n log n) preprocessing, O(log n) per query
- Space: O(n log n)

## When to Use
- Finding the k-th ancestor of a tree node, or the Lowest Common Ancestor.
- Simulating a functional graph (each node has exactly one successor) for a huge number of steps.

## Idea
Build a table `up[k][v]` = the 2^k-th ancestor/successor of v, via `up[k][v] = up[k-1][up[k-1][v]]`. To jump d steps, decompose d into powers of two (its binary representation) and chain the corresponding precomputed jumps.

## Related
- [[Lowest Common Ancestor (Binary Lifting)]]
- [[Sparse Table]]
