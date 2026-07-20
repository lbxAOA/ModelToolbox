---
category: Network Flow
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:39:12.857299+00:00
generated_by: claude
auto_generated: true
---

# Edmonds-Karp Algorithm

**Parent:** [[Graph Theory MOC]] → Network Flow
**Tags:** #graph-theory #network-flow #edmonds-karp

## Definition
Computes maximum flow by repeatedly finding an augmenting path from source to sink using BFS (shortest path by edge count) in the residual graph and pushing flow equal to its bottleneck capacity.

## Problem Recognition Signals
- "Maximum flow from source to sink" on a graph small/sparse enough that O(VE²) is acceptable, or as the conceptual entry point before implementing Dinic's for larger graphs.

## Complexity
- Time: O(V E²)
- Space: O(V + E)

## When to Use
- Small-to-medium flow networks, or when Dinic's added complexity isn't justified by the input size.

## Idea
A specific instantiation of the Ford-Fulkerson method that always augments along a BFS shortest augmenting path (in edge count) in the residual graph, which bounds the total number of augmentations to O(VE) (each augmentation saturates at least one edge, and shortest-path lengths are non-decreasing).

## Related
- [[Dinic's Algorithm]]
- [[Breadth-First Search (BFS)]]
