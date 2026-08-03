---
category: Minimum Spanning Tree
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:35:24.462836+00:00
generated_by: claude
auto_generated: true
---

# Kruskal's Algorithm

**Parent:** [[Graph Theory MOC]] → Minimum Spanning Tree
**Tags:** #graph-theory #mst #kruskal

## Definition
Builds a minimum spanning tree by sorting all edges by weight and greedily adding each edge that doesn't create a cycle, using a DSU to test connectivity.

## Problem Recognition Signals
- "Connect all nodes with minimum total edge cost" with edges given as an explicit list (as opposed to a dense/implicit graph, which might favor Prim's).
- Building a maximum spanning tree/forest (same algorithm, sort descending), or a Kruskal reconstruction tree for offline path-max/min queries.

## Complexity
- Time: O(E log E) dominated by sorting
- Space: O(V + E)

## When to Use
- Sparse graphs where the edge list is explicit and sorting is cheap relative to V².

## Idea
Sort all edges by weight ascending; for each edge in order, use DSU find to check if its endpoints are already connected — if not, union them and add the edge to the MST; stop once V-1 edges are added.

## Related
- [[Disjoint Set Union (DSU)]]
- [[Prim's Algorithm]]
- [[Greedy Algorithm]]
