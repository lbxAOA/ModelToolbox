---
category: Intersections & Sweeping
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:42:53.137671+00:00
generated_by: claude
auto_generated: true
---

# Line Segment Intersection

**Parent:** [[Computational Geometry MOC]] → Intersections & Sweeping
**Tags:** #computational-geometry #segment-intersection

## Definition
Determines whether (and where) two line segments intersect, using cross-product-based orientation tests (and a bounding-box check for collinear overlapping cases), and generalizes to finding all intersecting pairs among n segments via a sweep line in O(n log n + k) for k intersections.

## Problem Recognition Signals
- "Do two given segments cross?" (single pair, O(1) orientation test), or "find all pairs of segments that intersect among n given segments" (sweep-line signature).

## Complexity
- Time: O(1) for a single pair; O((n + k) log n) via sweep line for all pairs among n segments with k intersections
- Space: O(1) for a single pair, O(n) for the sweep-line version

## When to Use
- Single-pair intersection tests as a primitive inside larger geometric algorithms, or the sweep-line variant when many segments' pairwise intersections must all be found efficiently.

## Idea
Two segments intersect iff each segment's endpoints straddle the other segment's line (opposite-sign cross products on both sides), with special-case handling for collinear overlapping segments via bounding-box checks. For all-pairs intersection, sweep a vertical line left to right, maintaining the segments currently crossed in y-order, checking only newly-adjacent segments in that order for intersection (via a balanced BST/priority queue of events).

## Related
- [[2D Geometry Basics]]
- [[Sweep Line]]
