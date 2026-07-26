---
category: DP Fundamentals
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:13:24.750069+00:00
generated_by: claude
auto_generated: true
---

# DP Fundamentals

**Parent:** [[Dynamic Programming MOC]] → DP Fundamentals
**Tags:** #dynamic-programming #dp-fundamentals

## Definition
Solve a problem by defining a state that captures everything needed to make future decisions, and a transition that computes each state's value from previously-solved smaller/simpler states.

## Problem Recognition Signals
- "Maximize/minimize/count the number of ways" subject to constraints, where a brute-force recursion would revisit the same subproblem many times.
- The problem can be described by "the answer for state i depends on the answer for state(s) before i".

## Complexity
- Time: O(number of states × transition cost)
- Space: O(number of states), often reducible via rolling arrays

## When to Use
- Optimal substructure (optimal solution built from optimal solutions to subproblems) and overlapping subproblems (the same subproblem recurs) both hold.

## Idea
Identify the state (what varies between subproblems), the transition (recurrence relating a state to earlier states), the base case, and the evaluation order (so every state is computed after its dependencies). Implement top-down (recursion + memo) or bottom-up (iterative table fill).

## Related
- [[Memoized Search]]
- [[0-1 Knapsack]]
- [[Interval DP]]
