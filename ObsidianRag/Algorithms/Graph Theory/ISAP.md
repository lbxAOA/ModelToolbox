---
category: Network Flow
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:39:12.857299+00:00
generated_by: claude
auto_generated: true
---

# ISAP

**Parent:** [[Graph Theory MOC]] → Network Flow
**Tags:** #graph-theory #network-flow #isap

## Definition
"Improved Shortest Augmenting Path" — a maximum flow algorithm similar to Dinic's but avoiding repeated BFS re-layering per phase by maintaining and incrementally updating vertex distance labels ("gap optimization") as edges saturate.

## Problem Recognition Signals
- Same use cases as Dinic's algorithm; chosen as an alternative implementation with often-superior constant factors in practice for certain graph structures (fewer BFS passes).

## Complexity
- Time: O(V² E), same asymptotic bound as Dinic's, typically faster in practice due to avoiding repeated full BFS layering
- Space: O(V + E)

## When to Use
- Alternative to Dinic's for maximum flow when its typically-lower constant factor (from the gap optimization avoiding wasted work) matters, particularly on graphs with many saturating augmentations.

## Idea
Maintain a distance label per vertex (initialized via one reverse BFS from the sink); repeatedly DFS along edges from a vertex to one exactly one level closer to the sink, augmenting flow; when a vertex has no such valid edge, relabel it to 1 + the minimum label among its residual neighbors (retreating), using a "gap" check (no vertices remain at some label) to terminate early once the sink becomes provably unreachable.

## Related
- [[Dinic's Algorithm]]
