---
category: Offline Techniques
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:45:57.835091+00:00
generated_by: claude
auto_generated: true
---

# Parallel Binary Search

**Parent:** [[Miscellaneous MOC]] → Offline Techniques
**Tags:** #miscellaneous #parallel-binary-search #offline

## Definition
Solves many independent "binary search on the answer" queries simultaneously (offline) by advancing all queries' binary searches together in lockstep rounds, checking all queries' current midpoints against a shared, incrementally-built structure in one combined pass per round, instead of rebuilding that structure separately for each query's O(log n) individual binary search.

## Problem Recognition Signals
- "q queries, each needing a separate binary-search-on-the-answer, where checking a candidate answer for one query requires expensive shared state (e.g. replaying updates in order) that's wasteful to rebuild independently per query."

## Complexity
- Time: O((n + q) log n × cost of one shared "check" step), avoiding an extra factor of q from rebuilding shared state per query
- Space: O(n + q)

## When to Use
- Multiple binary-search-on-the-answer queries share an expensive-to-rebuild underlying structure/state (e.g. a DSU being unioned incrementally) that's naturally processed once in increasing order.

## Idea
Give every query its own [lo, hi] binary search range; each round, group queries by their current midpoint, replay the shared structure's updates once up to each needed point (in sorted order across all queries combined), check each query's condition against that shared state, and narrow every query's range accordingly; repeat rounds until every query's range converges.

## Related
- [[Binary Search]]
- [[Disjoint Set Union (DSU)]]
- [[Offline Algorithms]]
