---
category: Minimum Spanning Tree
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:35:24.462836+00:00
generated_by: claude
auto_generated: true
---

# Boruvka's Algorithm

**Parent:** [[Graph Theory MOC]] → Minimum Spanning Tree
**Tags:** #graph-theory #mst #boruvka

## Definition
Builds a minimum spanning forest in rounds: each round, every current component finds its cheapest outgoing edge, and all such edges are added simultaneously (merging components), repeating until one component remains.

## Problem Recognition Signals
- MST problems where edges aren't given explicitly but can be found implicitly/quickly per component (e.g. "cheapest edge from this component" answerable via a geometric or bitwise structure) — Boruvka's round structure (O(log V) rounds) combines well with such implicit-edge-finding structures.

## Complexity
- Time: O(E log V) explicitly, or faster when combined with a structure that finds each component's best outgoing edge in less than O(E) per round
- Space: O(V + E)

## When to Use
- As a building block when the "find the minimum outgoing edge per component" step can be accelerated by an auxiliary structure (e.g. a Linear XOR Basis for XOR-weighted MST, or a K-D Tree for Euclidean MST), making Boruvka's parallel round structure faster overall than Kruskal/Prim.

## Idea
Each round, every component scans its outgoing edges to find the single cheapest one leaving the component; add all these (deduplicated) cheapest edges to the MST simultaneously via DSU union, which provably at least halves the number of components each round, giving O(log V) rounds.

## Related
- [[Kruskal's Algorithm]]
- [[Disjoint Set Union (DSU)]]
