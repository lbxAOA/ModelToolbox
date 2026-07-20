---
category: Matching
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:39:12.857299+00:00
generated_by: claude
auto_generated: true
---

# Blossom Algorithm

**Parent:** [[Graph Theory MOC]] → Matching
**Tags:** #graph-theory #matching #blossom-algorithm #general-graph-matching

## Definition
Finds maximum matching in a general (not necessarily bipartite) graph by extending augmenting-path search to handle odd-length cycles ("blossoms") encountered during the search, contracting each blossom into a single super-vertex to continue the search.

## Problem Recognition Signals
- "Maximum matching" on a graph explicitly NOT stated/guaranteed to be bipartite — odd cycles can appear, breaking the simple bipartite augmenting-path approach.

## Complexity
- Time: O(V³) for the classic implementation (faster O(E√V) variants exist but are substantially more complex)
- Space: O(V + E)

## When to Use
- General graph matching where bipartiteness cannot be assumed.

## Idea
Run BFS/alternating-tree search for augmenting paths as in bipartite matching, but when an edge connects two vertices at the same "even" alternating-tree depth, an odd cycle (blossom) is found; contract it into one super-vertex (tracking how to "lift" the matching back out of the contraction afterward) and continue the search from the contracted graph.

## Related
- [[Hungarian Algorithm]]
- [[Tarjan's Strongly Connected Components]]
