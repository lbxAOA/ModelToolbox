---
category: Points & Regions
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:42:53.137671+00:00
generated_by: claude
auto_generated: true
---

# Pick's Theorem

**Parent:** [[Computational Geometry MOC]] → Points & Regions
**Tags:** #computational-geometry #picks-theorem #lattice-points

## Definition
Relates a simple polygon's area to its lattice points (points with integer coordinates): Area = I + B/2 - 1, where I is the number of interior lattice points and B is the number of boundary lattice points.

## Problem Recognition Signals
- "Count the number of lattice (integer-coordinate) points strictly inside/on the boundary of a polygon" combined with the polygon's area being easy to compute (via the shoelace formula), or vice versa.

## Complexity
- Time: O(n) given the polygon's vertices (to compute area via the shoelace formula and boundary points via gcd of edge coordinate differences)
- Space: O(1)

## When to Use
- Converting between a lattice polygon's area, interior lattice point count, and boundary lattice point count — knowing any two lets Pick's theorem give the third.

## Idea
Compute the polygon's area via the shoelace formula (sum of cross products of consecutive vertices / 2); compute B as the sum over edges of gcd(|dx|, |dy|) (the number of lattice points on each edge, minus overcounting at shared vertices); solve Pick's formula for whichever of I, B, Area is unknown.

## Related
- [[GCD and Extended Euclidean Algorithm]]
- [[2D Geometry Basics]]
