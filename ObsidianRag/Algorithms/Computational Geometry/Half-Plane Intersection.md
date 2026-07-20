---
category: Intersections & Sweeping
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:42:53.137671+00:00
generated_by: claude
auto_generated: true
---

# Half-Plane Intersection

**Parent:** [[Computational Geometry MOC]] → Intersections & Sweeping
**Tags:** #computational-geometry #half-plane-intersection

## Definition
Computes the (possibly empty or unbounded) convex polygon formed by the intersection of a set of half-planes, typically via an incremental or a sort-and-deque (angle-sorted) algorithm.

## Problem Recognition Signals
- "Find the region satisfying all of a set of linear inequalities" (feasible region of a linear program in 2D), or "find a point/region visible from/satisfying constraints from every one of n given directions/half-planes".

## Complexity
- Time: O(n log n) for the sort-and-deque algorithm
- Space: O(n)

## When to Use
- The problem reduces to intersecting many linear half-plane constraints into a single feasible convex region (often as the 2D case of a linear program, or a "common visible region" / "kernel of a polygon" problem).

## Idea
Represent each half-plane as a directed line (interior to its left); sort all half-planes by angle; process in angle order maintaining a deque of half-plane boundary lines forming the current intersection, popping lines from the back (and, once wrapped around, the front) whenever their intersection point with the new line falls outside the new half-plane.

## Related
- [[2D Geometry Basics]]
- [[Gaussian Elimination]]
