---
category: Union-Find
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:28:58.064828+00:00
generated_by: claude
auto_generated: true
---

# Disjoint Set Union (DSU)

**Parent:** [[Data Structures MOC]] → Union-Find
**Tags:** #data-structures #dsu #union-find

## Definition
Maintains a partition of elements into disjoint sets, supporting find (which set does x belong to) and union (merge two sets) in near-O(1) amortized time using path compression and union by rank/size.

## Problem Recognition Signals
- "Are elements x and y connected?", "count connected components", "process edges in order and detect when a cycle forms" (Kruskal's MST, offline connectivity).
- "Merge groups" phrasing without needing to enumerate group members, just membership/connectivity.

## Complexity
- Time: O(α(n)) amortized per operation (α = inverse Ackermann, effectively constant)
- Space: O(n)

## When to Use
- Incremental connectivity queries (edges only added, never removed), cycle detection while building a graph, or Kruskal's MST.

## Idea
Each element points to a parent; find(x) follows parent pointers to the root, compressing the path (pointing visited nodes directly to the root) along the way; union(x,y) attaches the smaller/shallower tree's root under the other's root (union by size/rank) to keep trees shallow.

## Related
- [[Kruskal's Algorithm]]
- [[2-SAT]]
- [[Offline Algorithms]]
