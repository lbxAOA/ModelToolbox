---
category: Intersections & Sweeping
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:42:53.137671+00:00
generated_by: claude
auto_generated: true
---

# Sweep Line

**Parent:** [[Computational Geometry MOC]] → Intersections & Sweeping
**Tags:** #computational-geometry #sweep-line

## Definition
A general technique that processes geometric events (points, segment endpoints, circle boundaries) in sorted order along one axis (imagining a line sweeping across the plane), maintaining a dynamic structure of "currently active" objects that's updated at each event.

## Problem Recognition Signals
- "Compute the total area/perimeter covered by a union of rectangles", "count all pairs of intersecting segments/circles", or any problem naturally described as "as x increases, track which objects are currently active".

## Complexity
- Time: O(n log n) typical, dominated by sorting events and maintaining the active-set structure (segment tree, balanced BST, etc.) per event
- Space: O(n)

## When to Use
- Geometric problems involving overlaps, unions, or nearest-neighbor relationships among many objects, where reducing 2D reasoning to a 1D "active set updated over sorted events" simplifies the algorithm.

## Idea
Sort all relevant events (e.g. segment/rectangle start and end x-coordinates) left to right; maintain an active-set data structure (segment tree over the y-axis for rectangle union area, a balanced BST ordered by y for segment intersection) that's updated (insert/remove/query) at each event in the sweep order.

## Related
- [[Line Segment Intersection]]
- [[Segment Tree]]
- [[Discretization]]
