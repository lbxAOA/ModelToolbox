---
category: Sorting Algorithms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:03:53.991853+00:00
generated_by: claude
auto_generated: true
---

# Bubble Sort

**Parent:** [[Algorithm Fundamentals MOC]] → Sorting Algorithms
**Tags:** #algorithm-fundamentals #sorting

## Definition
Repeatedly scan the array, swapping adjacent out-of-order elements, until no swaps are needed.

## Problem Recognition Signals
- Teaching/intro-level problem explicitly about "adjacent swaps" and n is very small.
- Rarely the intended solution for competitive problems with n > a few thousand.

## Complexity
- Time: O(n²) average/worst, O(n) best (already sorted)
- Space: O(1), in-place, stable

## When to Use
- Teaching/demonstration purposes, or tiny nearly-sorted arrays where simplicity matters more than speed.

## Idea
For each pass over the array, compare each adjacent pair and swap if out of order; the largest unsorted element "bubbles" to its correct position each pass. Stop early if a pass makes no swaps.

## Related
- [[Insertion Sort]]
- [[Selection Sort]]
