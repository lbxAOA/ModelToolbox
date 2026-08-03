---
category: Network Flow
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:39:12.857299+00:00
generated_by: claude
auto_generated: true
---

# Dinic's Algorithm

**Parent:** [[Graph Theory MOC]] → Network Flow
**Tags:** #graph-theory #network-flow #dinic

## Definition
Computes maximum flow faster than Edmonds-Karp by building a level graph (BFS layering by distance from source) each phase, then finding a blocking flow (saturating all shortest augmenting paths at once) via DFS within that level graph.

## Problem Recognition Signals
- "Maximum flow" with graph sizes too large for Edmonds-Karp's O(VE²) (e.g. V, E up to 10^4-10^5) — the default go-to max-flow algorithm in competitive programming.
- Bipartite matching problems modeled as flow (unit-capacity Dinic runs in O(E√V)).

## Complexity
- Time: O(V² E) general graphs, O(E√V) for unit-capacity graphs (e.g. bipartite matching)
- Space: O(V + E)

## When to Use
- The default choice for maximum flow in competitive programming due to strong practical performance across graph types.

## Idea
Repeat: BFS from the source to assign each vertex a level (distance), stopping if the sink is unreached; then DFS within the level graph (only following edges from level i to i+1) to find augmenting paths, pushing flow greedily and pruning "dead" edges (using an iterator/current-arc optimization to avoid re-scanning); repeat until no augmenting path exists in the level graph.

## Related
- [[Edmonds-Karp Algorithm]]
- [[Minimum Cost Maximum Flow]]
- [[Hopcroft-Karp Algorithm]]
