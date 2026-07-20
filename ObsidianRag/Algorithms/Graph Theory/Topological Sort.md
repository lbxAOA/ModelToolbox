---
category: Representation & Traversal
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:35:24.462836+00:00
generated_by: claude
auto_generated: true
---

# Topological Sort

**Parent:** [[Graph Theory MOC]] → Representation & Traversal
**Tags:** #graph-theory #topological-sort #dag

## Definition
Orders the vertices of a Directed Acyclic Graph so that every edge points from an earlier vertex to a later one in the ordering.

## Problem Recognition Signals
- "Task scheduling with prerequisites", "course ordering", "determine a valid build/compile order" — explicit dependency-ordering phrasing.
- Precondition for DAG DP (processing states in an order consistent with their dependencies).

## Complexity
- Time: O(V + E)
- Space: O(V)

## When to Use
- Any DAG where a linear processing order respecting dependencies is needed, including as a precursor to DAG DP.

## Idea
Kahn's algorithm: repeatedly remove (and output) vertices with in-degree 0, decrementing the in-degree of their neighbors, until the graph is empty (a remaining nonempty graph indicates a cycle). Alternatively, DFS-based: output vertices in reverse post-order.

## Related
- [[DAG DP]]
- [[Depth-First Search (DFS)]]
