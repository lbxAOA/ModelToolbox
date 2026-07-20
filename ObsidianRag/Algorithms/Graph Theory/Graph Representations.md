---
category: Representation & Traversal
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:35:24.462836+00:00
generated_by: claude
auto_generated: true
---

# Graph Representations

**Parent:** [[Graph Theory MOC]] → Representation & Traversal
**Tags:** #graph-theory #graph-representation

## Definition
The two standard ways to store a graph: an adjacency matrix (n×n array of edge weights/existence) for O(1) edge lookup, or an adjacency list (per-vertex list of neighbors/edges) for O(1) neighbor iteration and O(V+E) space.

## Problem Recognition Signals
- Any graph problem's first implementation decision; dense graphs (E close to V²) or frequent "does edge (u,v) exist" queries favor a matrix, sparse graphs favor a list.

## Complexity
- Time: O(1) edge existence check (matrix) vs. O(degree) (list); O(V) to iterate neighbors (matrix) vs. O(degree) (list)
- Space: O(V²) (matrix) vs. O(V+E) (list)

## When to Use
- Adjacency list: sparse graphs, need to iterate a vertex's neighbors (most graph algorithms). Adjacency matrix: dense graphs, need O(1) edge existence queries, or algorithms like Floyd-Warshall that naturally index by pairs.

## Idea
Adjacency list: array/vector of edge lists per vertex (or a single edge array with per-vertex head pointers, the "chain forward star" representation, for speed/memory). Adjacency matrix: 2D array indexed by (u, v) storing weight or boolean existence.

## Related
- [[Depth-First Search (DFS)]]
- [[Floyd-Warshall Algorithm]]
