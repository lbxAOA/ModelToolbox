---
category: Uninformed Search
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:07:41.154989+00:00
generated_by: claude
auto_generated: true
---

# Iterative Deepening DFS

**Parent:** [[Search MOC]] → Uninformed Search
**Tags:** #search #iterative-deepening

## Definition
Run DFS repeatedly with an increasing depth limit (0, 1, 2, ...), stopping as soon as the target is found within the current limit, combining DFS's low memory use with BFS's shortest-path guarantee.

## Problem Recognition Signals
- Very deep or infinite implicit search trees where BFS would use too much memory, but the shortest solution depth is unknown in advance.
- Puzzle-solving problems bounding the answer by "at most k moves" without knowing the tight k.

## Complexity
- Time: O(b^d) (asymptotically same order as BFS, with a constant-factor overhead from re-exploring shallow levels)
- Space: O(d), only the current DFS path

## When to Use
- Memory is the bottleneck (state space too large for BFS's frontier) but a shortest/minimal-depth solution is required.

## Idea
For depth limit L = 0, 1, 2, ..., perform a depth-limited DFS that stops descending past depth L; return the first solution found at the smallest L. Combine with heuristics for IDA*.

## Related
- [[Depth-First Search (DFS)]]
- [[Breadth-First Search (BFS)]]
- [[IDA*]]
