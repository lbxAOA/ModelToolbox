---
category: Enumeration & Simulation
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:03:53.991853+00:00
generated_by: claude
auto_generated: true
---

# Enumeration

**Parent:** [[Algorithm Fundamentals MOC]] → Enumeration & Simulation
**Tags:** #algorithm-fundamentals #enumeration

## Definition
Systematically generate and test every candidate in a (bounded) search space to find one that satisfies the problem's constraints.

## Problem Recognition Signals
- n is tiny (n ≤ ~20) or the answer space is small enough to brute force within the time limit.
- "Count/find all subsets/permutations/combinations satisfying..."
- No polynomial structure is apparent and constraints hint at 2^n or n! brute force.

## Complexity
- Time: O(size of search space × cost per check)
- Space: O(1) beyond bookkeeping

## When to Use
- The search space is small enough to exhaust within time limits.
- No smarter structure/property is apparent to prune the space.
- Often used to validate a faster algorithm or as a fallback for small subtasks.

## Idea
Loop over all possible values/combinations (nested loops, Cartesian product, or recursive generation), check the constraint, and record/return valid candidates. Pruning (early-exit on partial violations) turns plain enumeration into backtracking.

## Related
- [[Simulation]]
- [[Backtracking]]
- [[Meet in the Middle]]
