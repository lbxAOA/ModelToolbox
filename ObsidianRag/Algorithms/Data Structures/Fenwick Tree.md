---
category: Range Query Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:28:58.064828+00:00
generated_by: claude
auto_generated: true
---

# Fenwick Tree

**Parent:** [[Data Structures MOC]] → Range Query Structures
**Tags:** #data-structures #fenwick-tree #binary-indexed-tree

## Definition
A Binary Indexed Tree that supports point-update and prefix-sum query (and, via a difference-array trick, range-update/range-query) both in O(log n), using each index's lowest set bit to define an implicit tree over ranges.

## Problem Recognition Signals
- "q queries interleaved with updates: add v to position i, then ask for the sum of range [l, r]" — dynamic prefix-sum signature.
- Counting inversions, or any "count of elements ≤ x seen so far" problem via a Fenwick tree over value-ranks.

## Complexity
- Time: O(log n) per update or prefix-sum query
- Space: O(n)

## When to Use
- Interleaved point-updates and range-sum queries (or vice versa via the difference-array variant) — simpler and faster in practice than a segment tree when only sums (not arbitrary range operations) are needed.

## Idea
tree[i] stores the sum of a range of size (i & -i) ending at i; to update position i, repeatedly add to tree[i] and advance i += i & -i; to query prefix sum up to i, repeatedly add tree[i] and step i -= i & -i.

## Related
- [[Prefix Sum and Difference Array]]
- [[Segment Tree]]
- [[Insertion Sort]]
