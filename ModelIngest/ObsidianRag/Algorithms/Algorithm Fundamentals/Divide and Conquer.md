---
category: Recursion & Greedy
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:03:53.991853+00:00
generated_by: claude
auto_generated: true
---

# Divide and Conquer

**Parent:** [[Algorithm Fundamentals MOC]] → Recursion & Greedy
**Tags:** #algorithm-fundamentals #divide-and-conquer

## Definition
Split a problem into independent smaller subproblems of the same type, solve each recursively, then merge their solutions into the answer for the whole.

## Problem Recognition Signals
- "Count pairs / inversions / closest pair across the whole array" with n large (10^5-10^6).
- The answer for a range can be built from the answers of its two halves plus a cross-boundary merge step.
- Appears alongside sorting, counting inversions, or geometric closest-pair problems.

## Complexity
- Time: given by the Master Theorem, e.g. O(n log n) for T(n) = 2T(n/2) + O(n)
- Space: O(log n) to O(n) depending on merge step

## When to Use
- The problem can be split into non-overlapping (or easily combinable) subproblems.
- Merging partial answers is cheaper than solving the whole problem directly.

## Idea
Split the input in half (or into k parts), recurse on each part, then combine (e.g. merge two sorted halves, or combine closest-pair candidates across a splitting line). Classic examples: merge sort, quicksort, FFT, closest pair of points.

## Related
- [[Merge Sort]]
- [[Quicksort]]
- [[Closest Pair of Points]]
- [[Fast Fourier Transform (FFT)]]
