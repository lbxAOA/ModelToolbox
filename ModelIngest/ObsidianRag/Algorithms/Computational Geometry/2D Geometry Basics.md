---
category: Fundamentals
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:42:53.137671+00:00
generated_by: claude
auto_generated: true
---

# 2D Geometry Basics

**Parent:** [[Computational Geometry MOC]] → Fundamentals
**Tags:** #computational-geometry #vectors #cross-product

## Definition
The foundational toolkit for 2D geometry: representing points/vectors, and computing dot products (projection/angle) and cross products (signed area, orientation/turn direction) from coordinates.

## Problem Recognition Signals
- Any geometry problem's starting point: "given points/segments, determine relative position, angle, or orientation".
- "Determine if three points make a left turn / right turn / are collinear" (cross product sign).

## Complexity
- Time: O(1) per vector operation
- Space: O(1)

## When to Use
- As the primitive building block underlying essentially every other computational geometry algorithm (convex hull, polygon area, line intersection all reduce to cross/dot products).

## Idea
Cross product of vectors (x1,y1) and (x2,y2) is x1·y2 - x2·y1: positive means the second vector turns counterclockwise from the first (left turn), negative clockwise (right turn), zero means collinear; its absolute value is twice the area of the triangle they span. Dot product x1·x2 + y1·y2 gives |a||b|cos(θ), useful for projections and angle sign tests.

## Related
- [[Convex Hull (Monotone Chain)]]
- [[Point in Polygon]]
