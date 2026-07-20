---
category: Combinatorial Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:39:12.857299+00:00
generated_by: claude
auto_generated: true
---

# Hierholzer's Algorithm

**Parent:** [[Graph Theory MOC]] → Combinatorial Structures
**Tags:** #graph-theory #eulerian-path #hierholzer

## Definition
Constructs an Eulerian circuit or path (a walk using every edge exactly once) in O(V+E), by following edges until stuck in a closed loop, then splicing in additional loops found from any vertex on the current walk that still has unused edges.

## Problem Recognition Signals
- "Find a route/tour that uses every edge/road/domino exactly once" — the defining Eulerian-path/circuit signature (as opposed to Hamiltonian, which visits every vertex once).
- Existence check: an undirected graph has an Eulerian circuit iff connected and every vertex has even degree; an Eulerian path iff connected and exactly 0 or 2 vertices have odd degree.

## Complexity
- Time: O(V + E)
- Space: O(V + E)

## When to Use
- Constructing (not just checking existence of) a walk that traverses every edge exactly once.

## Idea
Start at any vertex (or one of the two odd-degree vertices for an Eulerian path) and greedily follow unused edges until returning to the start with no unused edges left (forming a closed sub-tour); while any vertex on the current tour still has unused edges, splice in a new sub-tour discovered from that vertex, merging it into the walk at that point, until every edge is used.

## Related
- [[Depth-First Search (DFS)]]
