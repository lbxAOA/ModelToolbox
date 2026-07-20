---
category: Classic Puzzles & Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:45:57.835091+00:00
generated_by: claude
auto_generated: true
---

# Chtholly Tree

**Parent:** [[Miscellaneous MOC]] → Classic Puzzles & Structures
**Tags:** #miscellaneous #chtholly-tree #color-segment-amortization

## Definition
An "ordered set of intervals with the same value" (color-segment) data structure that answers range-assign, range-query operations by merging equal-valued adjacent ranges into single nodes, achieving good amortized complexity specifically when range-assignment operations are frequent enough to keep the total interval count low ("Chtholly Tree"/"ODT", relying on the problem having many range-assign, or "even random", operations for its amortized bound to hold).

## Problem Recognition Signals
- Range-assign ("set every element in [l,r] to value x") combined with range aggregate queries (sum, k-th smallest, power sums), especially when the problem statement guarantees or implies many random/range-assign operations (a strong hint this data structure's amortized assumption is intended to hold).

## Complexity
- Time: amortized O((n + q) log n) when range-assign operations are frequent (the assumption the technique relies on); can degrade to O(n) per operation in adversarial cases without enough range-assigns
- Space: O(n) amortized (bounded by the number of distinct color segments, which range-assigns keep small)

## When to Use
- Range-assign-heavy problems (often explicitly signaled by the problem setter, e.g. "the array is generated randomly" or "many range set operations") where a segment tree with lazy propagation would need a more complex composed-tag design.

## Idea
Maintain a sorted set/map of maximal intervals each holding a single value; a range-assign first "splits" the intervals at the operation's boundaries (creating clean interval endpoints), then erases and replaces all fully-covered intervals with one new interval holding the assigned value — the amortized argument is that each assign operation can only ever decrease the total interval count by more than it increases it, over the long run, given enough assigns.

## Related
- [[Segment Tree with Lazy Propagation]]
- [[Linked List]]
