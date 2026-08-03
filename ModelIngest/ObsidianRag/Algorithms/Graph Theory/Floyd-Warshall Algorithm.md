---
category: Shortest Path
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:35:24.462836+00:00
generated_by: claude
auto_generated: true
---

# Floyd-Warshall Algorithm

**Parent:** [[Graph Theory MOC]] → Shortest Path
**Tags:** #graph-theory #shortest-path #floyd-warshall #all-pairs

## Definition
Computes shortest paths between all pairs of vertices simultaneously by considering each vertex as a potential intermediate point, in O(V³).

## Problem Recognition Signals
- "All-pairs shortest path" with V small (typically ≤ 400-1000), or "compute the transitive closure / reachability between all pairs".
- Small graph with many shortest-path queries between arbitrary pairs (answering each query in O(1) after preprocessing beats running Dijkstra from every source).

## Complexity
- Time: O(V³)
- Space: O(V²)

## When to Use
- All-pairs shortest paths needed and V is small enough for O(V³), especially with negative edges (but no negative cycles) where running Dijkstra from every vertex wouldn't apply.

## Idea
dist[i][j] initialized to the direct edge weight (or ∞); for each vertex k (as an allowed intermediate), update dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]) for all i, j — after considering all k, dist[i][j] is the true shortest path.

## Related
- [[Graph Representations]]
- [[Matrix Exponentiation]]
