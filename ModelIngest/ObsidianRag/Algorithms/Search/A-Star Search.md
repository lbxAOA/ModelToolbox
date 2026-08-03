---
category: Informed / Heuristic Search
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:09:59.295553+00:00
generated_by: claude
auto_generated: true
---

# A-Star Search

**Parent:** [[Search MOC]] → Informed / Heuristic Search
**Tags:** #search #a-star

## Definition
Best-first search that expands nodes in order of f(n) = g(n) + h(n), where g is the cost so far and h is an admissible heuristic estimate of the remaining cost, guaranteeing an optimal path when h never overestimates.

## Problem Recognition Signals
- Weighted shortest-path/pathfinding on a grid or graph where a good distance heuristic (Euclidean/Manhattan/Chebyshev) to a known goal exists.
- Puzzle-solving (e.g. 15-puzzle) explicitly mentioning a heuristic like "misplaced tiles" or "Manhattan distance".

## Complexity
- Time: O(E) in the worst case (degrades to Dijkstra with h=0), much better in practice with a strong heuristic
- Space: O(V) for the open/closed sets

## When to Use
- Single-target shortest path where an admissible heuristic meaningfully prunes the search versus plain Dijkstra.

## Idea
Use a priority queue keyed on g(n)+h(n); pop the lowest, relax its neighbors updating g, and push with their f-value, until the goal is popped. Equivalent to Dijkstra when h ≡ 0.

## Related
- [[Dijkstra's Algorithm]]
- [[IDA-Star]]
- [[Heuristic Search]]
