---
category: Convex Hull
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:42:53.137671+00:00
generated_by: claude
auto_generated: true
---

# Rotating Calipers

**Parent:** [[Computational Geometry MOC]] → Convex Hull
**Tags:** #computational-geometry #rotating-calipers

## Definition
A technique for computing extremal measurements over a convex polygon (diameter/farthest pair, minimum-area/perimeter bounding rectangle, width) by "rotating" a pair (or set) of parallel supporting lines around the hull, advancing pointers only forward, in linear time given the hull.

## Problem Recognition Signals
- "Find the two farthest points in a point set" (diameter of point set) or "find the minimum-area bounding rectangle of a point set" — problems requiring an extremal measurement over all directions/pairs on a convex hull.

## Complexity
- Time: O(n) given the convex hull (plus O(n log n) to compute the hull itself if not already available)
- Space: O(n)

## When to Use
- Any extremal-over-all-directions query on a convex polygon (diameter, width, minimum bounding rectangle), after first computing the convex hull.

## Idea
Maintain two (or more) pointers on the hull representing points touched by a pair of parallel supporting lines; advance whichever pointer increases a monotonic cross-product-based area/distance measure, exploiting convexity to guarantee each pointer only needs to move forward (never backward) as the calipers "rotate" a full turn around the hull.

## Related
- [[Convex Hull (Monotone Chain)]]
- [[Closest Pair of Points]]
