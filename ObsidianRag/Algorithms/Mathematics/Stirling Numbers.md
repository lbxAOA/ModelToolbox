---
category: Combinatorics
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Stirling Numbers

**Parent:** [[Mathematics MOC]] → Combinatorics
**Tags:** #mathematics #combinatorics #stirling-numbers

## Definition
Stirling numbers of the first kind count permutations of n elements by number of cycles; Stirling numbers of the second kind S(n,k) count ways to partition n distinct elements into k non-empty unlabeled subsets.

## Problem Recognition Signals
- "Partition n distinct items into exactly k non-empty groups" (second kind) or "count permutations with exactly k cycles" (first kind).
- Problems converting between "labeled" and "falling factorial" polynomial bases.

## Complexity
- Time: O(n·k) to build the full triangle via the recurrences, O(k log k) for a single S(n,k) via an inclusion-exclusion/NTT-based formula
- Space: O(n·k) for the triangle, O(1) extra for a single value via the closed form

## When to Use
- Explicit partition-into-k-groups or cycle-counting combinatorics problems, or converting between polynomial bases (ordinary powers vs. falling factorials) in generating-function work.

## Idea
Second kind recurrence: S(n,k) = k·S(n-1,k) + S(n-1,k-1) (add element n to an existing group, or start a new group). First kind (unsigned) recurrence: c(n,k) = (n-1)·c(n-1,k) + c(n-1,k-1) (element n joins an existing cycle in n-1 ways, or forms its own cycle).

## Related
- [[Permutations and Combinations]]
- [[Bell Numbers]]
