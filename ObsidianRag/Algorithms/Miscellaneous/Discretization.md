---
category: Array Techniques
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:45:57.835091+00:00
generated_by: claude
auto_generated: true
---

# Discretization

**Parent:** [[Miscellaneous MOC]] → Array Techniques
**Tags:** #miscellaneous #discretization #coordinate-compression

## Definition
Replaces a set of large/sparse values with their ranks in sorted order (a dense range 1..k for k distinct values), so structures requiring a small dense index range (Fenwick tree, counting sort) can be applied to originally huge or non-integer value ranges.

## Problem Recognition Signals
- "Values can be up to 10^9 (or are real numbers), but only up to n ≤ 10^5 distinct values actually appear" combined with needing an array/BIT/segment-tree indexed by value.
- "Compress coordinates" explicitly mentioned, or range-based problems (e.g. interval covering) where only interval endpoints matter, not the full numeric range.

## Complexity
- Time: O(n log n) to sort and deduplicate
- Space: O(n)

## When to Use
- The algorithm needs a dense small-range index (for an array, Fenwick tree, or counting sort) but the actual values are sparse or too large to index directly.

## Idea
Collect all values that will ever be queried/inserted, sort and deduplicate them, then map each original value to its index (rank) in this sorted list via binary search; use these compressed ranks as array/BIT indices instead of the raw values.

## Related
- [[Fenwick Tree]]
- [[Binary Search]]
- [[Prefix Sum and Difference Array]]
