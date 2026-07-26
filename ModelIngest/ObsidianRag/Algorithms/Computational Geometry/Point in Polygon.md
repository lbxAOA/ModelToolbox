---
category: Points & Regions
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:42:53.137671+00:00
generated_by: claude
auto_generated: true
---

# Point in Polygon

**Parent:** [[Computational Geometry MOC]] → Points & Regions
**Tags:** #computational-geometry #point-in-polygon

## Definition
Determines whether a given point lies inside, outside, or on the boundary of a (possibly non-convex) polygon, typically via the ray-casting (crossing number) method or the winding number method.

## Problem Recognition Signals
- "Determine if a point is inside a given polygon/region" — direct point-containment queries, potentially many against the same polygon.

## Complexity
- Time: O(n) per query for a simple polygon with n vertices (O(log n) with preprocessing if the polygon is convex)
- Space: O(n)

## When to Use
- Point-containment testing against an arbitrary simple polygon (ray casting), or specifically against a convex polygon where O(log n) binary-search-based testing is worth the extra implementation complexity.

## Idea
Ray casting: cast a ray from the point in a fixed direction (e.g. horizontal) and count how many polygon edges it crosses — an odd count means inside, even means outside (with careful handling of rays passing exactly through vertices). For convex polygons, binary search on the polar angle from an interior point to locate the point between two hull vertices in O(log n), then a single cross-product test.

## Related
- [[2D Geometry Basics]]
- [[Convex Hull (Monotone Chain)]]
