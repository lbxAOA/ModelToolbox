---
category: Linear Algebra
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:25:56.009258+00:00
generated_by: claude
auto_generated: true
---

# Matrix Exponentiation

**Parent:** [[Mathematics MOC]] → Linear Algebra
**Tags:** #mathematics #linear-algebra #matrix-exponentiation

## Definition
Represents a linear recurrence as a matrix multiplication (state_{i+1} = M × state_i) and computes the n-th term by fast-exponentiating M to the n-th power, rather than iterating n times.

## Problem Recognition Signals
- "Compute the n-th term of a linear recurrence (Fibonacci-like)" with n up to 10^9-10^18.
- DP transitions that are linear in the previous state(s) and need to be applied an astronomically large number of times.

## Complexity
- Time: O(k³ log n) for a k×k transition matrix and n applications
- Space: O(k²)

## When to Use
- A DP or recurrence has a small, fixed-size linear transition applied a huge number of times.

## Idea
Express the recurrence as a matrix-vector product; build the k×k transition matrix M once, then compute M^n via fast exponentiation (repeated squaring using matrix multiplication as the associative operation), and multiply by the base-case vector.

## Related
- [[Fast Exponentiation]]
- [[DP Fundamentals]]
