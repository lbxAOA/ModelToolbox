---
category: Shortest Path
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:35:24.462836+00:00
generated_by: claude
auto_generated: true
---

# Bellman-Ford Algorithm

**Parent:** [[Graph Theory MOC]] → Shortest Path
**Tags:** #graph-theory #shortest-path #bellman-ford

## Definition
Computes single-source shortest paths even with negative edge weights (and detects negative cycles) by relaxing every edge V-1 times.

## Problem Recognition Signals
- "Shortest path with possibly negative edge weights" or "detect whether a negative cycle exists (e.g. an arbitrage opportunity)".

## Complexity
- Time: O(V × E)
- Space: O(V)

## When to Use
- Negative edge weights are present, or negative-cycle detection is explicitly required.

## Idea
Initialize distances (0 for source, ∞ otherwise); repeat V-1 times: for every edge (u,v,w), relax dist[v] = min(dist[v], dist[u]+w). If any edge can still be relaxed on a V-th pass, a negative cycle reachable from the source exists.

## Related
- [[SPFA]]
- [[Dijkstra's Algorithm]]
