---
category: Sorting Algorithms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:03:53.991853+00:00
generated_by: claude
auto_generated: true
---

# Merge Sort

**Parent:** [[Algorithm Fundamentals MOC]] → Sorting Algorithms
**Tags:** #algorithm-fundamentals #sorting #divide-and-conquer

## Definition
Recursively split the array in half, sort each half, then merge the two sorted halves into one sorted array.

## Problem Recognition Signals
- "Count the number of inversions in an array" (classic merge-sort-counting signature).
- Need guaranteed O(n log n) regardless of adversarial input, or a stable sort.

## Complexity
- Time: O(n log n) in all cases (worst, average, best)
- Space: O(n) auxiliary array for merging

## When to Use
- Guaranteed O(n log n) is required regardless of input distribution.
- Stable sort is needed, or sorting linked lists (O(1) extra space possible there).
- Counting inversions during the merge step.

## Idea
Split the array into two halves, recursively sort each, then merge by repeatedly taking the smaller of the two current front elements into the output array.

## Related
- [[Divide and Conquer]]
- [[Quicksort]]
- [[CDQ Divide and Conquer]]
