---
category: Tree Algorithms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:39:12.857299+00:00
generated_by: claude
auto_generated: true
---

# Lowest Common Ancestor (Binary Lifting)

**Parent:** [[Graph Theory MOC]] → Tree Algorithms
**Tags:** #graph-theory #lca #binary-lifting #tree

## Definition
Finds the lowest common ancestor of two nodes in a rooted tree using binary lifting: precomputed 2^k-th ancestor tables let both nodes be raised to the same depth and then jumped upward together in O(log n) per query.

## Problem Recognition Signals
- "Find the LCA of two nodes" with many queries (online, one at a time, can't batch offline).
- Distance-between-two-nodes-in-a-tree queries (dist(u,v) = depth[u]+depth[v]-2·depth[lca(u,v)]).

## Complexity
- Time: O(n log n) preprocessing, O(log n) per query
- Space: O(n log n)

## When to Use
- Online LCA queries (queries arrive one at a time and must be answered immediately, ruling out offline methods).

## Idea
Precompute depth and 2^k-th ancestor tables via [[Binary Lifting]]; to find LCA(u,v), first raise the deeper node to the same depth as the other using binary-decomposed jumps, then jump both nodes up together by decreasing powers of two as long as they land on different ancestors, until one more step would make them equal (that common parent is the LCA).

## Related
- [[Binary Lifting]]
- [[Lowest Common Ancestor (Tarjan Offline)]]
- [[Euler Tour and Sparse Table LCA]]
