---
category: Range Query Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:28:58.064828+00:00
generated_by: claude
auto_generated: true
---

# Segment Tree with Lazy Propagation

**Parent:** [[Data Structures MOC]] → Range Query Structures
**Tags:** #data-structures #segment-tree #lazy-propagation

## Definition
Extends the segment tree to support range updates (e.g. add v to every element in [l,r]) in O(log n) by deferring ("lazily") the update's effect on a node's descendants until they're actually visited.

## Problem Recognition Signals
- "Range update (add/assign to a range), range query" — both operations act on ranges, ruling out plain point-update segment trees or Fenwick trees (without the harder 2-BIT trick).

## Complexity
- Time: O(log n) per range update or range query
- Space: O(n)

## When to Use
- Both updates and queries are range-based, and the update (add, assign, etc.) can be composed/deferred (applied to a whole subtree's aggregate directly, with children updated only on demand).

## Idea
Each node holds a "lazy" tag representing a pending update not yet pushed to its children; a range update that fully covers a node's range updates the node's aggregate directly and sets/merges its lazy tag instead of recursing further; before descending into a node's children for any other operation, "push down" the lazy tag to them first.

## Related
- [[Segment Tree]]
- [[Prefix Sum and Difference Array]]
