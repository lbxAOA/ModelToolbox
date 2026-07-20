---
category: Sorting Algorithms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:03:53.991853+00:00
generated_by: claude
auto_generated: true
---

# Shell Sort

**Parent:** [[Algorithm Fundamentals MOC]] → Sorting Algorithms
**Tags:** #algorithm-fundamentals #sorting

## Definition
A generalization of insertion sort that first sorts elements far apart by a decreasing gap sequence, progressively reducing the gap to 1.

## Problem Recognition Signals
- Rarely the intended solution in modern OI; mostly seen in textbook contexts asking specifically for a gap-sequence sort.

## Complexity
- Time: O(n log² n) to O(n^1.5) depending on the gap sequence (worse gap sequences degrade toward O(n²))
- Space: O(1), in-place, not stable

## When to Use
- Medium-sized arrays where a simple, low-overhead, in-place sort faster than plain insertion sort is wanted without implementing quicksort/heapsort.

## Idea
For each gap value in a decreasing sequence (e.g. Knuth's 3k+1 or Sedgewick's sequence), perform an insertion sort where elements are compared/swapped gap positions apart instead of adjacent, ending with gap = 1 (a final ordinary insertion sort pass on an already mostly-sorted array).

## Related
- [[Insertion Sort]]
