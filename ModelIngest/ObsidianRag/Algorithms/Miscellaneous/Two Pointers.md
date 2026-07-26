---
category: Array Techniques
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:45:57.835091+00:00
generated_by: claude
auto_generated: true
---

# Two Pointers

**Parent:** [[Miscellaneous MOC]] → Array Techniques
**Tags:** #miscellaneous #two-pointers

## Definition
Maintains two indices into a sequence (moving independently or in lockstep, typically both only ever moving forward) to avoid an inner loop that would otherwise make an O(n) per-position scan into an O(n²) total algorithm.

## Problem Recognition Signals
- "Find a subarray/substring/pair satisfying a condition" where the condition is monotonic as one pointer advances (e.g. "smallest window with sum ≥ k", "count pairs with sum ≤ x" in a sorted array).
- "Merge two sorted arrays/sequences" or partition-style array problems.

## Complexity
- Time: O(n) (each pointer moves at most n times total)
- Space: O(1)

## When to Use
- A brute-force nested-loop solution's inner loop only ever needs to move forward as the outer loop advances (never backward), i.e. the search window/boundary is monotonic.

## Idea
Maintain a window or pair of pointers [l, r]; advance one pointer to satisfy/violate a condition, and advance the other in response, ensuring each pointer only moves forward across the whole algorithm so total pointer movement is O(n), not O(n²).

## Related
- [[Merge Sort]]
- [[Binary Search]]
- [[Discretization]]
