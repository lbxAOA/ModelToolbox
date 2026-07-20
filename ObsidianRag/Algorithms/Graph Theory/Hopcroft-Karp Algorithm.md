---
category: Matching
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:39:12.857299+00:00
generated_by: claude
auto_generated: true
---

# Hopcroft-Karp Algorithm

**Parent:** [[Graph Theory MOC]] → Matching
**Tags:** #graph-theory #matching #hopcroft-karp #bipartite

## Definition
Finds maximum bipartite matching faster than the simple augmenting-path (Hungarian/Kuhn's) approach by finding a maximal set of shortest, vertex-disjoint augmenting paths (via BFS layering) each phase, and augmenting along all of them simultaneously (via DFS).

## Problem Recognition Signals
- "Maximum bipartite matching" on large sparse graphs where plain Kuhn's algorithm's O(VE) is too slow (V, E large enough that the sqrt(V) factor improvement matters).

## Complexity
- Time: O(E √V)
- Space: O(V + E)

## When to Use
- Large sparse bipartite graphs needing maximum (unweighted) matching faster than O(VE).

## Idea
Each phase: BFS from all unmatched left vertices to layer the graph and find the shortest augmenting path length; then DFS to find a maximal set of vertex-disjoint augmenting paths of exactly that length, flipping all of them; repeat until no augmenting path exists — the number of phases is bounded by O(√V).

## Related
- [[Hungarian Algorithm]]
- [[Breadth-First Search (BFS)]]
- [[Dinic's Algorithm]]
