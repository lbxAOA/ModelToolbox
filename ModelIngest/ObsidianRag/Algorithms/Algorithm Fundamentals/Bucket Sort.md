---
category: Sorting Algorithms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:03:53.991853+00:00
generated_by: claude
auto_generated: true
---

# Bucket Sort

**Parent:** [[Algorithm Fundamentals MOC]] → Sorting Algorithms
**Tags:** #algorithm-fundamentals #sorting

## Definition
Distribute elements into a number of buckets covering ranges of the input domain, sort each bucket individually, then concatenate.

## Problem Recognition Signals
- Values are floating point or uniformly distributed reals/integers over a known range.
- Problem hints "values uniformly distributed" or asks for an O(n) expected-time sort of such data.

## Complexity
- Time: O(n + k) average when input is uniformly distributed, O(n²) worst case if all elements land in one bucket
- Space: O(n + k)

## When to Use
- Input is (roughly) uniformly distributed over a known range, e.g. floating-point numbers in [0, 1).

## Idea
Map each element to a bucket index based on its value, insert into that bucket (often keeping each bucket sorted via insertion sort), then concatenate all buckets in order.

## Related
- [[Counting Sort]]
- [[Insertion Sort]]
