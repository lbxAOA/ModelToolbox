---
category: Range Query Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:28:58.064828+00:00
generated_by: claude
auto_generated: true
---

# Li Chao Tree

**Parent:** [[Data Structures MOC]] → Range Query Structures
**Tags:** #data-structures #li-chao-tree #convex-hull-trick

## Definition
A segment-tree-over-the-x-domain structure that maintains a set of inserted lines (or line segments) and answers "maximum/minimum value at x" queries in O(log n), generalizing the Convex Hull Trick to cases where slopes/queries aren't monotonic.

## Problem Recognition Signals
- DP optimization problems of the "min/max over j of a line evaluated at x[i]" shape (same signature as Convex Hull Trick) but where lines are inserted and queried in arbitrary (non-monotonic) order.

## Complexity
- Time: O(log n) per line insertion or point query (O(log² n) for segment insertion)
- Space: O(n)

## When to Use
- The Convex Hull Trick's monotonicity requirements (on slopes and/or query order) don't hold, but a segment-tree-based structure over the x-range is acceptable.

## Idea
Each segment-tree node owns one "best so far" line for its x-range's midpoint; inserting a new line recursively compares it against the node's current line at the midpoint and at the range endpoints, keeping whichever dominates at the midpoint and recursing into the half-range where the other might still win.

## Related
- [[Convex Hull Trick (Slope Optimization)]]
- [[Segment Tree]]
