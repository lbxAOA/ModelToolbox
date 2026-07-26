---
category: Sorting Algorithms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:03:53.991853+00:00
generated_by: claude
auto_generated: true
---

# Heap Sort

**Parent:** [[Algorithm Fundamentals MOC]] → Sorting Algorithms
**Tags:** #algorithm-fundamentals #sorting

## Definition
Build a max-heap from the array, then repeatedly extract the maximum and place it at the end of the unsorted region.

## Problem Recognition Signals
- Need guaranteed O(n log n) worst case with O(1) extra memory (embedded/memory-constrained context).
- Problem also needs a priority queue elsewhere in the solution.

## Complexity
- Time: O(n log n) worst case, guaranteed
- Space: O(1), in-place, not stable

## When to Use
- Guaranteed O(n log n) with O(1) extra space is needed (unlike merge sort's O(n) space).
- As the underlying structure whenever a priority queue is needed alongside sorting.

## Idea
Heapify the array into a binary max-heap (O(n)), then n times swap the root (maximum) with the last unsorted element and sift-down the new root to restore the heap property.

## Related
- [[Binary Heap]]
- [[Quicksort]]
