---
category: Connectivity
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:35:24.462836+00:00
generated_by: claude
auto_generated: true
---

# Tarjan's Strongly Connected Components

**Parent:** [[Graph Theory MOC]] → Connectivity
**Tags:** #graph-theory #scc #tarjan

## Definition
Finds all strongly connected components (maximal sets of vertices each pair of which is mutually reachable) of a directed graph in a single DFS pass, using discovery times and "low-link" values.

## Problem Recognition Signals
- "Find groups of mutually reachable vertices in a directed graph", or as a preprocessing step to condense a graph into a DAG of SCCs before running DAG DP.
- 2-SAT solutions (SCC of the implication graph determines satisfiability).

## Complexity
- Time: O(V + E)
- Space: O(V)

## When to Use
- Directed graph mutual-reachability grouping, condensing cycles into single DAG nodes, or as the core subroutine of 2-SAT.

## Idea
DFS while maintaining a discovery-time counter and a stack of "currently active" vertices; each vertex's low-link value is the minimum discovery time reachable via tree edges and back edges to still-on-stack vertices; when a vertex's low-link equals its own discovery time, it roots an SCC — pop the stack down to (and including) it to output that component.

## Related
- [[Kosaraju's Algorithm]]
- [[2-SAT]]
- [[Depth-First Search (DFS)]]
