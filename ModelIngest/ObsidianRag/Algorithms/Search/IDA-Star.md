---
category: Informed / Heuristic Search
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:09:59.295553+00:00
generated_by: claude
auto_generated: true
---

# IDA-Star

**Parent:** [[Search MOC]] → Informed / Heuristic Search
**Tags:** #search #ida-star

## Definition
Iterative deepening DFS where the depth bound is replaced by an f = g + h cost bound, increasing the bound each iteration to the smallest f-value that exceeded the previous bound.

## Problem Recognition Signals
- Puzzle search problems (15-puzzle, Rubik's-cube-like state spaces) where the state space is too large for A*'s memory but a good heuristic exists.
- "Find the minimum number of moves" with a huge implicit search tree and available heuristic.

## Complexity
- Time: similar order to A* but with repeated re-exploration overhead per iteration
- Space: O(d), just the current path — far less than A*'s open/closed sets

## When to Use
- A* runs out of memory (huge state space) but a good admissible heuristic is available; willing to trade some recomputation for linear memory.

## Idea
Run a DFS that prunes any branch once g+h exceeds the current bound; if no solution is found, raise the bound to the minimum f-value that was pruned and retry, until the goal is reached.

## Related
- [[A-Star Search]]
- [[Iterative Deepening DFS]]
