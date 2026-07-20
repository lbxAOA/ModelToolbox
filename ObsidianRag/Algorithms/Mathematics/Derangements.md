---
category: Combinatorics
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Derangements

**Parent:** [[Mathematics MOC]] → Combinatorics
**Tags:** #mathematics #combinatorics #derangements

## Definition
A derangement is a permutation with no fixed points (no element maps to itself); the number of derangements of n elements, D(n), satisfies D(n) = (n-1)·(D(n-1) + D(n-2)) and D(n) = n!·Σ_{i=0}^n (-1)^i/i!.

## Problem Recognition Signals
- "Count permutations where no element is in its original position" — the classic "hat-check problem" / "no one gets their own letter back" phrasing.
- Generalized versions: "count permutations with exactly k fixed points" (combine with combinations: choose the k fixed points, derange the rest).

## Complexity
- Time: O(n) to compute via the recurrence, given precomputed factorials for the closed-form alternative
- Space: O(n)

## When to Use
- Direct derangement counting, or as a component when inclusion-exclusion decomposes a harder permutation-counting problem into derangement-like sub-counts.

## Idea
Derive via inclusion-exclusion over "element i is a fixed point": D(n) = n!·Σ(-1)^i/i!, or use the linear recurrence D(n) = (n-1)(D(n-1)+D(n-2)) with D(0)=1, D(1)=0 for an O(n) tabulation.

## Related
- [[Inclusion-Exclusion Principle]]
- [[Permutations and Combinations]]
