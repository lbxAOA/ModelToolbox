---
category: Randomized Techniques
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:45:57.835091+00:00
generated_by: claude
auto_generated: true
---

# Simulated Annealing

**Parent:** [[Miscellaneous MOC]] → Randomized Techniques
**Tags:** #miscellaneous #simulated-annealing #randomized

## Definition
A randomized local-search heuristic for optimization problems that, like hill climbing, moves toward better neighboring solutions, but also probabilistically accepts worse moves (with probability decreasing over time via a "temperature" schedule) to escape local optima.

## Problem Recognition Signals
- Optimization problems (minimize/maximize some cost) where no polynomial exact algorithm is apparent, constraints are small-to-medium, and the problem allows partial credit / near-optimal answers (common in problems explicitly awarding partial scores).
- Continuous optimization over a geometric configuration (e.g. "find the point minimizing sum of distances to given points").

## Complexity
- Time: heuristic — typically run for a fixed time budget, no correctness/optimality guarantee
- Space: O(1) to O(n) depending on state representation

## When to Use
- As a fallback heuristic when no exact polynomial algorithm is known/needed and the scoring allows near-optimal or randomized-with-multiple-restarts solutions.

## Idea
Start from an initial solution and a high "temperature"; repeatedly propose a random neighboring solution, accepting it immediately if better, or with probability exp(-Δcost/temperature) if worse; gradually lower the temperature (cooling schedule) so the search becomes more greedy over time; often restarted multiple times with different random seeds within the time budget.

## Related
- [[Greedy Algorithm]]
- [[Random Incremental Construction]]
