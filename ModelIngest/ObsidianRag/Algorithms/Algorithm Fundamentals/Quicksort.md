---
category: Sorting Algorithms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:03:53.991853+00:00
generated_by: claude
auto_generated: true
---

# Quicksort

**Parent:** [[Algorithm Fundamentals MOC]] → Sorting Algorithms
**Tags:** #algorithm-fundamentals #sorting #divide-and-conquer

## Definition
Pick a pivot, partition the array into elements less-than and greater-than the pivot, then recursively sort each partition.

## Problem Recognition Signals
- "Sort n up to 10^6-10^7 elements in-place with minimal memory."
- Need average-case fast sorting or a k-th order statistic (quickselect variant).

## Complexity
- Time: O(n log n) average, O(n²) worst case (bad pivot choices, e.g. already-sorted input with a naive pivot)
- Space: O(log n) average recursion depth, in-place partitioning

## When to Use
- General-purpose in-memory sorting where average-case speed and low memory overhead matter (most standard library sorts use a quicksort/introsort hybrid).
- Randomized or median-of-three pivot selection avoids worst-case behavior on adversarial input.

## Idea
Choose a pivot (ideally random or median-of-three), partition the array so all elements < pivot come before it and all elements > pivot come after (Lomuto or Hoare partition scheme), then recurse on each side.

## Related
- [[Divide and Conquer]]
- [[Merge Sort]]
- [[Meet in the Middle]]
