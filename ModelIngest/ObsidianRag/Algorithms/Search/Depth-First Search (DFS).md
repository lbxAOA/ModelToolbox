---
category: Uninformed Search
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:07:41.154989+00:00
generated_by: claude
auto_generated: true
---

# Depth-First Search (DFS)

**Parent:** [[Search MOC]] → Uninformed Search
**Tags:** #search #dfs

## Definition
Explore a graph/tree by going as deep as possible along each branch before backtracking, using a stack (explicit or via recursion).

## Problem Recognition Signals
- "Find any path", "is it connected", "count connected components", or "detect a cycle" in a graph/grid.
- Tree traversal problems (preorder/postorder), flood-fill on a grid, topological ordering.
- Any problem needing entry/exit timestamps (Euler tour) for subtree queries.

## Complexity
- Time: O(V + E)
- Space: O(V) for the visited set and recursion stack

## When to Use
- Exploring all reachable nodes, detecting cycles, computing connected components, topological sort, or when recursion structure matches the problem naturally (e.g. subtree aggregation).

## Idea
From a start node, recursively (or with an explicit stack) visit an unvisited neighbor, marking nodes visited to avoid revisiting, and backtrack when no unvisited neighbors remain.

## Related
- [[Breadth-First Search (BFS)]]
- [[Backtracking]]
- [[Topological Sort]]
- [[Tarjan's Strongly Connected Components]]
