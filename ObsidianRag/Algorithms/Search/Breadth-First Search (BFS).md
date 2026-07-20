---
category: Uninformed Search
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:07:41.154989+00:00
generated_by: claude
auto_generated: true
---

# Breadth-First Search (BFS)

**Parent:** [[Search MOC]] → Uninformed Search
**Tags:** #search #bfs

## Definition
Explore a graph level by level from a source, visiting all nodes at distance d before any node at distance d+1, using a FIFO queue.

## Problem Recognition Signals
- "Shortest path/minimum number of moves in an unweighted graph or grid."
- "Minimum number of steps/operations to transform state A into state B" where each operation is a unit-cost edge.
- Multi-source shortest distance ("nearest of several sources").

## Complexity
- Time: O(V + E)
- Space: O(V)

## When to Use
- Shortest path in an unweighted graph (or one with uniform edge weights).
- Level-order traversal, or multi-source "nearest special cell" problems (seed the queue with all sources at distance 0).

## Idea
Push the start node(s) into a queue with distance 0; repeatedly pop the front, and for each unvisited neighbor mark its distance as current+1 and push it, until the queue is empty or the target is found.

## Related
- [[Depth-First Search (DFS)]]
- [[Bidirectional Search]]
- [[0-1 BFS (Dijkstra's Algorithm with deque)]]
- [[Dijkstra's Algorithm]]
