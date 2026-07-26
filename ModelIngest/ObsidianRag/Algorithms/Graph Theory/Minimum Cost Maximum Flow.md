---
category: Network Flow
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:39:12.857299+00:00
generated_by: claude
auto_generated: true
---

# Minimum Cost Maximum Flow

**Parent:** [[Graph Theory MOC]] → Network Flow
**Tags:** #graph-theory #network-flow #min-cost-flow #mcmf

## Definition
Among all maximum flows (or all flows of a given target value) from source to sink, finds the one with minimum total cost, where each edge has both a capacity and a per-unit cost.

## Problem Recognition Signals
- "Assign/route flow subject to capacity constraints while minimizing total cost" — assignment problems with costs, transportation problems, or flow problems explicitly mentioning both capacity and cost per edge.

## Complexity
- Time: O(F × (V + E) log V) using SPFA/Dijkstra-with-potentials for F total flow units (each augmentation pushes along the cheapest augmenting path), or O(V E F) with a simpler Bellman-Ford-based approach
- Space: O(V + E)

## When to Use
- Flow problems where minimizing cost (not just achieving max flow) is the objective, e.g. assignment problems modeled as flow.

## Idea
Repeatedly find the cheapest augmenting path from source to sink in the residual graph (via SPFA/Bellman-Ford to handle negative residual-edge costs, or Dijkstra with Johnson's potentials for speed), push the maximum flow possible along it, and repeat until no augmenting path remains (or the target flow value is reached).

## Related
- [[Dinic's Algorithm]]
- [[Bellman-Ford Algorithm]]
- [[Hungarian Algorithm]]
