---
category: Recursion & Greedy
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:03:53.991853+00:00
generated_by: claude
auto_generated: true
---

# Recursion

**Parent:** [[Algorithm Fundamentals MOC]] → Recursion & Greedy
**Tags:** #algorithm-fundamentals #recursion

## Definition
A function solves a problem by calling itself on smaller subproblems until a base case is reached.

## Problem Recognition Signals
- Problem is naturally defined on trees, nested brackets, or fractal/self-similar structures.
- "Define f(n) in terms of f(n-1), f(n-2), ..."
- Small n (recursion depth safe) or a clear shrinking step exists.

## Complexity
- Time: depends on recurrence relation (e.g. T(n) = a·T(n/b) + f(n))
- Space: O(depth of recursion) for the call stack

## When to Use
- The problem has a natural self-similar/recursive structure (trees, nested structures, divide-and-conquer).
- A clear base case and a way to shrink the problem toward it exist.

## Idea
Define the base case(s) that can be answered directly, and the recursive case that reduces the problem to one or more smaller instances of itself, combining their results. Watch for stack depth limits on large inputs; convert to iteration or add memoization if subproblems repeat.

## Related
- [[Divide and Conquer]]
- [[Memoized Search]]
- [[Backtracking]]
