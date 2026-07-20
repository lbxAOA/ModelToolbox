---
category: Convex Hull
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:42:53.137671+00:00
generated_by: claude
auto_generated: true
---

# Graham Scan

**Parent:** [[Computational Geometry MOC]] → Convex Hull
**Tags:** #computational-geometry #convex-hull #graham-scan

## Definition
Computes the convex hull by picking a pivot point guaranteed to be on the hull (e.g. lowest y-coordinate), sorting the remaining points by polar angle around it, then scanning in that angular order with a turn-based stack, popping non-convex points.

## Problem Recognition Signals
- Same use cases as Monotone Chain (convex hull computation); Graham Scan is the historically earlier, angle-sort-based alternative.

## Complexity
- Time: O(n log n) (dominated by the polar-angle sort)
- Space: O(n)

## When to Use
- Convex hull computation; functionally equivalent to Monotone Chain, differing mainly in implementation style (polar angle sort vs. x-coordinate sort).

## Idea
Pick the point with the lowest y-coordinate (breaking ties by lowest x) as the pivot (guaranteed to be a hull vertex); sort all other points by polar angle around the pivot; scan in that order maintaining a stack, popping the top whenever the last two stack points and the current point make a non-counterclockwise turn.

## Related
- [[Convex Hull (Monotone Chain)]]
- [[2D Geometry Basics]]
