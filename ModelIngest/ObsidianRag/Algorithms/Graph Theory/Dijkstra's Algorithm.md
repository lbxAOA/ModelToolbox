---
category: Shortest Path
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:35:24.462836+00:00
generated_by: claude
auto_generated: true
---

# Dijkstra's Algorithm

**Parent:** [[Graph Theory MOC]] → Shortest Path
**Tags:** #graph-theory #shortest-path #dijkstra

## Definition
Computes single-source shortest paths in a graph with non-negative edge weights, by repeatedly extending the shortest-path tree with the closest not-yet-finalized vertex via a priority queue.

## Problem Recognition Signals
- "Shortest path from a source in a weighted graph" with all weights explicitly non-negative.
- Grid/graph pathfinding problems with varying edge costs (not unit weight, which would suggest plain BFS instead).

## Complexity
- Time: O((V + E) log V) with a binary heap
- Space: O(V + E)

## When to Use
- Single-source shortest path with non-negative weights (the most common shortest-path scenario in practice).

## Idea
Maintain tentative distances (∞ initially, 0 for source) and a priority queue keyed by tentative distance; repeatedly pop the vertex with smallest tentative distance, finalize it, and relax (potentially improve) its neighbors' distances, pushing improved ones back into the queue.

## Related
- [[A-Star Search]]
- [[Bellman-Ford Algorithm]]
- [[Binary Heap]]
