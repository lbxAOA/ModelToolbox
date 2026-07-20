---
category: Structural DP
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:13:24.750069+00:00
generated_by: claude
auto_generated: true
---

# DAG DP

**Parent:** [[Dynamic Programming MOC]] → Structural DP
**Tags:** #dynamic-programming #dag-dp #graph

## Definition
Dynamic programming where the states and transitions form a Directed Acyclic Graph; processing states in topological order guarantees each state's dependencies are already resolved.

## Problem Recognition Signals
- "Longest/shortest path in a DAG", "longest increasing subsequence" (viewed as a DAG of index precedence), or any DP whose dependency structure isn't a simple linear/interval order.
- Explicit graph given as a DAG (or implied acyclic by problem constraints) asking for optimal path / counting paths.

## Complexity
- Time: O(V + E) after topological sort
- Space: O(V)

## When to Use
- The recurrence's dependency graph is acyclic but not necessarily linear/interval-shaped (arbitrary DAG structure).

## Idea
Topologically sort the DAG, then process nodes in that order, relaxing/updating each successor's DP value from its predecessors — identical in spirit to Bellman-Ford relaxation but done once per edge since there's no need to iterate for cycles.

## Related
- [[Topological Sort]]
- [[DP Fundamentals]]
