---
category: Uninformed Search
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:07:41.154989+00:00
generated_by: claude
auto_generated: true
---

# Bidirectional Search

**Parent:** [[Search MOC]] → Uninformed Search
**Tags:** #search #bidirectional-search

## Definition
Run two simultaneous BFS/searches, one forward from the start and one backward from the goal, and stop when their explored frontiers meet.

## Problem Recognition Signals
- Shortest path/transformation between two explicitly known states (both start and target given), with a huge branching factor.
- "Minimum number of moves to turn configuration A into configuration B" (e.g. puzzle states) where forward search alone is too slow.

## Complexity
- Time: O(b^(d/2)) vs. O(b^d) for one-directional search, where b is branching factor and d is the distance
- Space: O(b^(d/2)) to store both frontiers

## When to Use
- Both the start and goal states are known explicitly and the state graph is implicit with high branching factor (search trees, puzzles).

## Idea
Expand the forward frontier from the start and the backward frontier from the goal in lockstep (or alternating), checking after each expansion whether the two frontiers intersect; the total path length is the sum of both search depths at the meeting point.

## Related
- [[Breadth-First Search (BFS)]]
- [[Meet in the Middle]]
