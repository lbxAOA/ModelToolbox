---
category: Combinatorics
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Catalan Numbers

**Parent:** [[Mathematics MOC]] → Combinatorics
**Tags:** #mathematics #combinatorics #catalan-numbers

## Definition
The n-th Catalan number C_n = (1/(n+1))·C(2n, n) counts balanced bracket sequences of length 2n, binary trees with n internal nodes, ways to triangulate a convex (n+2)-gon, and many other equivalent combinatorial structures.

## Problem Recognition Signals
- "Count the number of valid parenthesis/bracket sequences", "count the number of distinct binary search trees with n nodes", "count monotonic lattice paths that don't cross the diagonal".

## Complexity
- Time: O(n) to compute one value given precomputed factorials, O(n) to tabulate all C_0..C_n via the recurrence C_n = Σ C_i·C_{n-1-i}
- Space: O(n)

## When to Use
- Recognizing a problem as isomorphic to balanced-bracket-sequence counting or one of Catalan numbers' other combinatorial interpretations (binary trees, non-crossing partitions, lattice paths).

## Idea
Compute directly via the closed form C_n = C(2n,n)/(n+1) using factorials and modular inverses, or build up via the recurrence C_n = Σ_{i=0}^{n-1} C_i · C_{n-1-i} (splitting at the first return to zero).

## Related
- [[Permutations and Combinations]]
- [[Interval DP]]
