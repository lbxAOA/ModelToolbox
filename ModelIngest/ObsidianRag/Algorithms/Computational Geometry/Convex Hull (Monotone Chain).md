---
category: Convex Hull
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:42:53.137671+00:00
generated_by: claude
auto_generated: true
---

# Convex Hull (Monotone Chain)

**Parent:** [[Computational Geometry MOC]] → Convex Hull
**Tags:** #computational-geometry #convex-hull #monotone-chain

## Definition
Computes the convex hull (smallest convex polygon containing all points) of a point set in O(n log n) by sorting points by x-coordinate (then y) and building the lower and upper hull chains independently via a cross-product turn test.

## Problem Recognition Signals
- "Find the convex hull of a set of points", or any geometry problem that reduces to it (smallest enclosing shape, farthest pair of points via rotating calipers, etc.).

## Complexity
- Time: O(n log n) (dominated by sorting)
- Space: O(n)

## When to Use
- Direct convex hull computation, or as a preprocessing step for rotating calipers (diameter, minimum bounding rectangle) and other hull-based queries.

## Idea
Sort points by (x, y); build the lower hull by scanning left to right, appending points and popping the last point whenever the last three make a non-counterclockwise turn; build the upper hull symmetrically scanning right to left; concatenate both chains (minus duplicated endpoints) for the full hull.

## Related
- [[2D Geometry Basics]]
- [[Graham Scan]]
- [[Rotating Calipers]]
