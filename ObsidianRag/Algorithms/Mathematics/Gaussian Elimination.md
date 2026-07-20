---
category: Linear Algebra
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:25:56.009258+00:00
generated_by: claude
auto_generated: true
---

# Gaussian Elimination

**Parent:** [[Mathematics MOC]] → Linear Algebra
**Tags:** #mathematics #linear-algebra #gaussian-elimination

## Definition
Solves a system of linear equations (or computes rank/determinant/inverse of a matrix) by row-reducing the augmented matrix to row-echelon form using elementary row operations.

## Problem Recognition Signals
- Explicit system of linear equations to solve, or "expected value" DP problems where transitions loop back (self-referential expectation equations) requiring a linear system.
- Determining linear (in)dependence of a set of vectors over the reals or a finite field.

## Complexity
- Time: O(n³) for an n×n system
- Space: O(n²)

## When to Use
- Solving linear systems directly, computing matrix rank/determinant, or resolving DP-with-cycles (expected value/probability) problems algebraically.

## Idea
For each column, select a pivot row (partial pivoting for numerical stability over reals, or any nonzero entry over a finite field/mod p), swap it into position, scale it to make the pivot 1, then eliminate that column's entries from all other rows using row subtraction; back-substitute once in triangular form.

## Related
- [[Probability DP]]
- [[Linear (XOR) Basis]]
