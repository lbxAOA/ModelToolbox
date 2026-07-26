---
category: Sorting Algorithms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:03:53.991853+00:00
generated_by: claude
auto_generated: true
---

# Radix Sort

**Parent:** [[Algorithm Fundamentals MOC]] → Sorting Algorithms
**Tags:** #algorithm-fundamentals #sorting

## Definition
Sort integers digit by digit (least-significant to most-significant, or vice versa), using a stable sub-sort (typically counting sort) at each digit position.

## Problem Recognition Signals
- Sorting huge numbers of fixed-width integers/strings (e.g. 32-bit keys) where comparison sorts' log factor matters.
- Suffix array construction (radix sort on rank pairs) is a strong hint.

## Complexity
- Time: O(d·(n + k)) for d digits and base/range k
- Space: O(n + k)

## When to Use
- Sorting large numbers of fixed-width integers or strings where the digit count is small relative to n.

## Idea
Repeatedly apply a stable sort keyed on each digit, starting from the least significant digit and moving to the most significant; stability across passes guarantees the final order is correct.

## Related
- [[Counting Sort]]
