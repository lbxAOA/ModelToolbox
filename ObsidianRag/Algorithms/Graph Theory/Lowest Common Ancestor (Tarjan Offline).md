---
category: Tree Algorithms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:39:12.857299+00:00
generated_by: claude
auto_generated: true
---

# Lowest Common Ancestor (Tarjan Offline)

**Parent:** [[Graph Theory MOC]] → Tree Algorithms
**Tags:** #graph-theory #lca #tarjan-offline #tree

## Definition
Answers all LCA queries in a single DFS pass (given all queries are known in advance) using a DSU to track, for each subtree just finished, which ancestor any query partner should currently resolve to.

## Problem Recognition Signals
- All LCA queries are given upfront (offline) rather than arriving interactively — explicit "answer all q queries" batch phrasing.

## Complexity
- Time: O((n + q) α(n)) for n nodes and q queries
- Space: O(n + q)

## When to Use
- All queries are known before processing starts, making the simpler and often faster offline DSU-based method preferable to online binary lifting.

## Idea
DFS the tree; upon finishing a subtree rooted at v, union v's DSU set into its parent's; whenever a query partner u of the current node v has already been visited, LCA(u,v) is the DSU-find root of u (which, due to how unions have happened so far, resolves to their common ancestor at the current point in the traversal).

## Related
- [[Disjoint Set Union (DSU)]]
- [[Lowest Common Ancestor (Binary Lifting)]]
- [[Offline Algorithms]]
