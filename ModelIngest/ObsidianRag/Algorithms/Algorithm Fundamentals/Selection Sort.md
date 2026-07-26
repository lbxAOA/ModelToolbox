---
category: Sorting Algorithms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:03:53.991853+00:00
generated_by: claude
auto_generated: true
---

# Selection Sort

**Parent:** [[Algorithm Fundamentals MOC]] → Sorting Algorithms
**Tags:** #algorithm-fundamentals #sorting

## Definition
Repeatedly find the minimum of the unsorted remainder and swap it into place at the front.

## Problem Recognition Signals
- Explicit constraint on minimizing the number of swaps/writes rather than comparisons.
- Small n, introductory sorting context.

## Complexity
- Time: O(n²) in all cases
- Space: O(1), in-place, not stable (in the naive swap-based form)

## When to Use
- Minimizing the number of swaps matters more than comparisons (e.g. writes are expensive).

## Idea
For position i from 0 to n-1, scan the remaining unsorted suffix for its minimum element and swap it into position i.

## Related
- [[Bubble Sort]]
- [[Insertion Sort]]
