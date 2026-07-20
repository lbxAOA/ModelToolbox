---
category: Points & Regions
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:42:53.137671+00:00
generated_by: claude
auto_generated: true
---

# Closest Pair of Points

**Parent:** [[Computational Geometry MOC]] → Points & Regions
**Tags:** #computational-geometry #closest-pair #divide-and-conquer

## Definition
Finds the minimum distance between any two points in a set in O(n log n) via divide-and-conquer, splitting by x-coordinate and carefully checking only a narrow strip of candidates near the split line.

## Problem Recognition Signals
- "Find the minimum distance between any two of n given points" with n large enough (10^4-10^6) that the naive O(n²) all-pairs check is too slow.

## Complexity
- Time: O(n log n)
- Space: O(n)

## When to Use
- Minimum pairwise distance queries on a static point set where n rules out brute force.

## Idea
Sort points by x; recursively find the closest pair in the left and right halves (giving current best distance d); then check only points within distance d of the vertical split line, sorted by y — a key geometric lemma bounds the number of such candidates that need comparing to a small constant per point, keeping the merge step O(n).

## Related
- [[Divide and Conquer]]
- [[K-D Tree]]
- [[Rotating Calipers]]
