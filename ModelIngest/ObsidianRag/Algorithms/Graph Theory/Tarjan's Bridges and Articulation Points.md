---
category: Connectivity
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:35:24.462836+00:00
generated_by: claude
auto_generated: true
---

# Tarjan's Bridges and Articulation Points

**Parent:** [[Graph Theory MOC]] → Connectivity
**Tags:** #graph-theory #bridges #articulation-points #tarjan

## Definition
Finds bridges (edges whose removal disconnects the graph) and articulation points/cut vertices (vertices whose removal disconnects the graph) in an undirected graph via a single DFS using discovery times and low-link values.

## Problem Recognition Signals
- "Find critical connections/roads whose removal disconnects the network" (bridges), or "find critical servers/intersections" (articulation points) — network-reliability/robustness phrasing.

## Complexity
- Time: O(V + E)
- Space: O(V)

## When to Use
- Identifying single points of failure (edges or vertices) in an undirected network.

## Idea
DFS tracking discovery time disc[v] and low-link low[v] (minimum discovery time reachable via tree edges and back edges, excluding the edge back to the immediate parent); an edge (u,v) is a bridge iff low[v] > disc[u]; a non-root vertex u is an articulation point iff some child v has low[v] ≥ disc[u] (root is an articulation point iff it has ≥ 2 DFS children).

## Related
- [[Biconnected Components]]
- [[Depth-First Search (DFS)]]
