---
category: Connectivity
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:35:24.462836+00:00
generated_by: claude
auto_generated: true
---

# Kosaraju's Algorithm

**Parent:** [[Graph Theory MOC]] → Connectivity
**Tags:** #graph-theory #scc #kosaraju

## Definition
Finds strongly connected components using two DFS passes: one on the original graph to compute a finishing-time order, one on the transposed (reversed-edges) graph processed in reverse finishing-time order, where each DFS tree in the second pass is exactly one SCC.

## Problem Recognition Signals
- Same use cases as Tarjan's SCC algorithm; Kosaraju's is often preferred when it's conceptually simpler to reason about (two clear passes) even though it needs the graph transpose explicitly.

## Complexity
- Time: O(V + E)
- Space: O(V + E) (needs to store both the graph and its transpose)

## When to Use
- Same as Tarjan's SCC; pick whichever implementation style (single-pass low-link vs. two-pass transpose) is more familiar.

## Idea
DFS the original graph, pushing each vertex onto a stack when it finishes (post-order); then DFS the transposed graph, always starting from the topmost unvisited stack vertex — each resulting DFS tree is exactly one SCC.

## Related
- [[Tarjan's Strongly Connected Components]]
- [[Depth-First Search (DFS)]]
