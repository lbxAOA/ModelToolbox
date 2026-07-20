---
category: Range Query Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:28:58.064828+00:00
generated_by: claude
auto_generated: true
---

# Segment Tree Beats

**Parent:** [[Data Structures MOC]] → Range Query Structures
**Tags:** #data-structures #segment-tree-beats

## Definition
An extension of the segment tree supporting non-classical range operations like "chmin" (set every element in a range to min(current, x)) alongside range sum/max queries, using an amortized-complexity argument (Ji Driver's technique) rather than a straightforward lazy tag.

## Problem Recognition Signals
- "Range chmin/chmax update (clip every element in a range to at most/at least x) combined with range sum or range max queries" — operations that don't compose into a simple lazy tag.

## Complexity
- Time: O((n + q) log² n) amortized, via a potential-function argument bounding total "second maximum" merges
- Space: O(n)

## When to Use
- Range chmin/chmax combined with range aggregate queries, where a standard lazy-propagation segment tree can't represent the update compactly.

## Idea
Each node tracks the max, second-max, and count of max elements in its range; a chmin(x) update only recurses into a node if x is strictly between the max and second-max (updating the max directly otherwise, or recursing fully if x ≤ second-max), which an amortized analysis shows totals O(log² n) per operation across all updates.

## Related
- [[Segment Tree with Lazy Propagation]]
