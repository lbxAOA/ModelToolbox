---
category: Minimum Spanning Tree
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:35:24.462836+00:00
generated_by: claude
auto_generated: true
---

# Prim's Algorithm

**Parent:** [[Graph Theory MOC]] → Minimum Spanning Tree
**Tags:** #graph-theory #mst #prim

## Definition
Builds a minimum spanning tree by growing a single tree from an arbitrary start vertex, repeatedly adding the cheapest edge connecting the tree to a new vertex, using a priority queue (very similar in structure to Dijkstra's algorithm).

## Problem Recognition Signals
- "Connect all nodes with minimum total cost" on a dense graph (e.g. given as a distance matrix, like a Euclidean MST on points) where Kruskal's edge sort would be O(V² log V) instead of using an O(V²) dense-Prim variant.

## Complexity
- Time: O((V+E) log V) with a binary heap (sparse graphs), O(V²) with a simple array-based version (dense graphs, often faster in practice for dense inputs)
- Space: O(V + E)

## When to Use
- Dense graphs (near-complete, e.g. point sets with all pairwise distances) where the O(V²) array-based Prim's beats Kruskal's sort.

## Idea
Maintain, for every vertex outside the current tree, the minimum edge weight connecting it to the tree; repeatedly select the outside vertex with the smallest such value, add it (and its connecting edge) to the tree, and update its neighbors' minimum connecting weight.

## Related
- [[Kruskal's Algorithm]]
- [[Dijkstra's Algorithm]]
- [[Binary Heap]]
