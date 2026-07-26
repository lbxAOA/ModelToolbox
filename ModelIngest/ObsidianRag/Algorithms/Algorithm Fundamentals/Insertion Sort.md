---
category: Sorting Algorithms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:03:53.991853+00:00
generated_by: claude
auto_generated: true
---

# Insertion Sort

**Parent:** [[Algorithm Fundamentals MOC]] → Sorting Algorithms
**Tags:** #algorithm-fundamentals #sorting

## Definition
Build the sorted array one element at a time, inserting each new element into its correct position among the already-sorted prefix.

## Problem Recognition Signals
- "Elements arrive one at a time, keep them sorted" (online insertion).
- Counting inversions with small-to-medium n, or as a component of a hybrid sort.

## Complexity
- Time: O(n²) worst/average, O(n) best (already sorted)
- Space: O(1), in-place, stable

## When to Use
- Small arrays, nearly-sorted data, or as the base case for hybrid sorts (e.g. Timsort, introsort switch to insertion sort below a size threshold).
- Online sorting (elements arrive one at a time).

## Idea
For each element, shift larger elements in the sorted prefix one position right until the correct gap is found, then insert. Can be sped up with binary search for the insertion point (binary insertion sort) or with a Fenwick tree/BIT for counting inversions.

## Related
- [[Shell Sort]]
- [[Merge Sort]]
