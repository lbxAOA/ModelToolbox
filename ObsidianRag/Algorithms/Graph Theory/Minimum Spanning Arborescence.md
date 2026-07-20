---
category: Minimum Spanning Tree
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:35:24.462836+00:00
generated_by: claude
auto_generated: true
---

# Minimum Spanning Arborescence

**Parent:** [[Graph Theory MOC]] → Minimum Spanning Tree
**Tags:** #graph-theory #minimum-spanning-arborescence #directed-mst

## Definition
The directed-graph analogue of MST: given a directed graph and a root, finds the minimum-total-weight set of edges forming a spanning tree where every vertex is reachable from the root via directed edges (solved by the Chu-Liu/Edmonds algorithm).

## Problem Recognition Signals
- "Minimum cost to make every node reachable from a fixed root via directed edges" — explicitly directed graph with asymmetric edge costs, ruling out plain Kruskal/Prim.

## Complexity
- Time: O(VE) for the straightforward Chu-Liu/Edmonds implementation, O(E log V) with more advanced data structures
- Space: O(V + E)

## When to Use
- Directed spanning tree (arborescence) problems where edges have direction-dependent costs and a designated root is given.

## Idea
For each non-root vertex, select its cheapest incoming edge; if this selection contains no cycle, it's the answer. If a cycle forms, contract it into a single super-vertex (adjusting incoming/outgoing edge weights to account for the edge replaced within the cycle) and recurse on the contracted graph, expanding the solution back out afterward.

## Related
- [[Kruskal's Algorithm]]
- [[Tarjan's Strongly Connected Components]]
