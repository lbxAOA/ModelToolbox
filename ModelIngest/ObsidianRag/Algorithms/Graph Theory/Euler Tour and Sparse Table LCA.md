---
category: Tree Algorithms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:39:12.857299+00:00
generated_by: claude
auto_generated: true
---

# Euler Tour and Sparse Table LCA

**Parent:** [[Graph Theory MOC]] → Tree Algorithms
**Tags:** #graph-theory #lca #euler-tour #sparse-table

## Definition
Reduces LCA queries to a Range Minimum Query by recording a DFS Euler tour of the tree (each node's depth each time it's visited/left) and observing that the LCA of two nodes is the shallowest node between their first occurrences in the tour, answerable in O(1) via a Sparse Table.

## Problem Recognition Signals
- Online LCA queries where O(1) per query (after O(n log n) preprocessing) is specifically desired, beating binary lifting's O(log n) per query.

## Complexity
- Time: O(n log n) preprocessing (or O(n) with more advanced ±1 RMQ techniques), O(1) per query
- Space: O(n log n)

## When to Use
- A very large number of LCA queries where shaving the log factor from binary lifting's per-query cost meaningfully matters.

## Idea
DFS the tree recording (node, depth) at every visit (including returns from children) into a linear Euler tour array of size 2n-1; record each node's first occurrence index; LCA(u,v) is then the node with minimum depth in the tour's subrange between u and v's first occurrences, answered via a Sparse Table over the tour's depth sequence.

## Related
- [[Sparse Table]]
- [[Cartesian Tree]]
- [[Lowest Common Ancestor (Binary Lifting)]]
