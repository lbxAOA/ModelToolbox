---
category: Ranges & Search
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:03:53.991853+00:00
generated_by: claude
auto_generated: true
---

# Binary Search

**Parent:** [[Algorithm Fundamentals MOC]] → Ranges & Search
**Tags:** #algorithm-fundamentals #binary-search

## Definition
Repeatedly halve a sorted (or otherwise monotonic) search space by comparing the midpoint against the target condition, discarding the half that cannot contain the answer.

## Problem Recognition Signals
- "Minimize/maximize x such that condition(x) holds" where condition is monotonic in x (classic "binary search on the answer").
- "Find the smallest/largest value satisfying..." over a sorted array, or "minimize the maximum of ..." / "maximize the minimum of ...".

## Complexity
- Time: O(log n)
- Space: O(1)

## When to Use
- Searching a sorted array for a value or insertion point.
- "Binary search on the answer": the feasibility of a candidate answer is monotonic (if x works, every value on one side of x also works), even if the underlying array isn't sorted.

## Idea
Maintain a range [lo, hi]; compute mid = (lo+hi)/2, test the monotonic predicate at mid, and shrink the range to the half consistent with the answer, until lo and hi converge. Careful with off-by-one boundaries and integer overflow in mid computation.

## Related
- [[Parallel Binary Search]]
- [[WQS Binary Search]]
- [[Meet in the Middle]]
