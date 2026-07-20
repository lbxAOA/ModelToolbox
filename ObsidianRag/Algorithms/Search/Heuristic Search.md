---
category: Informed / Heuristic Search
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:09:59.295553+00:00
generated_by: claude
auto_generated: true
---

# Heuristic Search

**Parent:** [[Search MOC]] → Informed / Heuristic Search
**Tags:** #search #heuristic-search

## Definition
Guide exploration using a heuristic function that estimates the remaining cost/distance to the goal, prioritizing states that look most promising.

## Problem Recognition Signals
- Puzzle or pathfinding problems where a natural distance estimate exists (e.g. Manhattan distance, misplaced tiles).
- "Find optimal or near-optimal solution efficiently" in a state space too large for exhaustive search.

## Complexity
- Time: highly heuristic-dependent, in the best case close to O(d) with a perfect heuristic; worst case unchanged from uninformed search
- Space: depends on the specific algorithm chosen (A*, greedy best-first, etc.)

## When to Use
- A domain-specific admissible (or approximate) distance-to-goal estimate is available to prune the search.

## Idea
Maintain a priority queue ordered by (cost-so-far + heuristic estimate) or by heuristic alone (greedy best-first), always expanding the most promising node next. The quality/admissibility of the heuristic determines optimality and speed.

## Related
- [[A-Star Search]]
- [[IDA-Star]]
