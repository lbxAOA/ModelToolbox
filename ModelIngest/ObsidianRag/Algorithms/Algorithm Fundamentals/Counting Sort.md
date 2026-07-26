---
category: Sorting Algorithms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:03:53.991853+00:00
generated_by: claude
auto_generated: true
---

# Counting Sort

**Parent:** [[Algorithm Fundamentals MOC]] → Sorting Algorithms
**Tags:** #algorithm-fundamentals #sorting

## Definition
Sort integers by counting occurrences of each distinct key value, then reconstructing the sorted order from those counts.

## Problem Recognition Signals
- Keys are small integers (e.g. 0 to 10^5) even though n is large — "values are bounded by a small constant/range".
- Need a stable O(n) sort as a building block (e.g. inside radix sort or bucketed counting).

## Complexity
- Time: O(n + k) where k is the range of key values
- Space: O(n + k)

## When to Use
- Keys are integers within a small, known range (k not much larger than n).
- A stable sort is needed as a subroutine (e.g. inside radix sort).

## Idea
Count occurrences of each value into a count array, take a prefix sum over counts to get each value's final position range, then place elements into the output array in a stable pass (often iterating input in reverse to preserve stability).

## Related
- [[Radix Sort]]
- [[Bucket Sort]]
