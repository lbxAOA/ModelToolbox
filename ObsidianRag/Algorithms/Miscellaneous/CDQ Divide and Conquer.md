---
category: Offline Techniques
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:45:57.835091+00:00
generated_by: claude
auto_generated: true
---

# CDQ Divide and Conquer

**Parent:** [[Miscellaneous MOC]] → Offline Techniques
**Tags:** #miscellaneous #cdq-divide-and-conquer #offline

## Definition
An offline divide-and-conquer technique that solves problems with multiple sorted dimensions (e.g. "3D partial order" problems: time, then x, then y) by recursively splitting on one dimension (typically time/index) and, in the merge step, counting cross-contributions between the two halves using a simpler structure (like a Fenwick tree) since one dimension is already implicitly sorted by the recursion.

## Problem Recognition Signals
- "For each element, count/aggregate over other elements that come before it in time/index AND satisfy an additional 1D or 2D condition" (e.g. 3D dominance counting: i < j, a[i] < a[j], b[i] < b[j]).
- Problems that would need a 2D or 3D data structure (like a segment tree of Fenwick trees) but can be reduced to one fewer dimension by processing offline.

## Complexity
- Time: O(n log² n) typical (an O(log n) factor from the divide-and-conquer recursion, another from a Fenwick tree used in the merge step)
- Space: O(n)

## When to Use
- Multi-dimensional partial-order counting/aggregation problems (3D dominance, inversions with extra constraints) solvable offline, reducing one dimension via merge-sort-style divide and conquer.

## Idea
Recursively split the elements (in their given, e.g. time, order) into two halves; recursively solve each half; in the merge step, sort both halves by the second dimension (e.g. via merge sort) and sweep through, using a Fenwick tree over the third dimension to count/aggregate contributions from left-half elements to right-half elements.

## Related
- [[Merge Sort]]
- [[Fenwick Tree]]
- [[Divide and Conquer]]
