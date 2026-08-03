---
category: Matching
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:39:12.857299+00:00
generated_by: claude
auto_generated: true
---

# Hungarian Algorithm

**Parent:** [[Graph Theory MOC]] → Matching
**Tags:** #graph-theory #matching #hungarian-algorithm #bipartite

## Definition
Finds a maximum-cardinality matching in a bipartite graph (or, in its weighted form, a minimum/maximum-cost perfect matching, also known as the assignment problem) via repeated augmenting-path search.

## Problem Recognition Signals
- "Assign n workers to n tasks to maximize/minimize total cost/benefit, one-to-one" — the classic assignment problem.
- "Maximum matching in a bipartite graph" (unweighted version).

## Complexity
- Time: O(VE) for unweighted maximum bipartite matching (Kuhn's algorithm), O(V³) for the weighted assignment problem
- Space: O(V + E)

## When to Use
- Bipartite matching/assignment problems; for unweighted maximum matching on large sparse bipartite graphs, Hopcroft-Karp is asymptotically faster.

## Idea
Unweighted (Kuhn's/augmenting path): for each left vertex, DFS for an augmenting path (an alternating path ending at an unmatched right vertex), flipping matched/unmatched edges along it if found. Weighted (assignment problem): maintain vertex "labels" (potentials) and repeatedly find augmenting paths in the equality subgraph, adjusting labels when none exists, converging to a minimum-cost perfect matching.

## Related
- [[Hopcroft-Karp Algorithm]]
- [[Minimum Cost Maximum Flow]]
