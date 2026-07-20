---
category: Ranges & Search
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:03:53.991853+00:00
generated_by: claude
auto_generated: true
---

# Prefix Sum and Difference Array

**Parent:** [[Algorithm Fundamentals MOC]] → Ranges & Search
**Tags:** #algorithm-fundamentals #prefix-sum

## Definition
A prefix sum array precomputes running totals so any range sum can be answered in O(1); a difference array is its inverse, letting range-add updates be applied in O(1) and recovered via prefix sum.

## Problem Recognition Signals
- "q queries, each asking for the sum of a range [l, r]" with a static array.
- "Add v to every element in range [l, r], q times, output the final array" — all updates offline before reading.

## Complexity
- Time: O(n) to build, O(1) per range-sum query or per range-add update
- Space: O(n)

## When to Use
- Many range-sum queries over a static array (prefix sum).
- Many range-add updates followed by reading the final array once (difference array).
- Generalizes to 2D (matrix prefix sums) and to a Fenwick Tree/Segment Tree when both updates and queries must interleave dynamically.

## Idea
Prefix sum: `pre[i] = pre[i-1] + a[i]`, so sum(l..r) = `pre[r] - pre[l-1]`. Difference array: `diff[i] = a[i] - a[i-1]`; to add v to range [l, r], do `diff[l] += v; diff[r+1] -= v`, then a prefix sum over diff reconstructs the updated array.

## Related
- [[Fenwick Tree]]
- [[Segment Tree]]
- [[Discretization]]
