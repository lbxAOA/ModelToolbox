---
category: Offline Techniques
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:45:57.835091+00:00
generated_by: claude
auto_generated: true
---

# Mo's Algorithm

**Parent:** [[Miscellaneous MOC]] → Offline Techniques
**Tags:** #miscellaneous #mos-algorithm #offline

## Definition
Answers many offline range queries on a static array in O((n+q)√n) by sorting queries into blocks (by left endpoint's block, then right endpoint) and maintaining a running answer that's incrementally extended/shrunk as the current range slides between consecutive queries.

## Problem Recognition Signals
- "q offline range queries (e.g. 'count distinct values in [l, r]', 'count pairs with a given property in [l,r]') on a static array" where the query answer can be incrementally updated in O(1) as a single element is added/removed from the range.

## Complexity
- Time: O((n + q) √n)
- Space: O(n + q)

## When to Use
- Range queries on a static array (no updates) where a segment tree doesn't naturally support the query (e.g. "count distinct elements"), but adding/removing a single element from a maintained range is cheap.

## Idea
Sort queries by (left endpoint's block of size √n, then right endpoint, alternating direction per block for a small constant-factor speedup); move current l/r pointers one step at a time toward each query's range, incrementally updating the running answer as each element enters/leaves, achieving amortized O(√n) pointer movement per query.

## Related
- [[Sqrt Decomposition]]
- [[Mo's Algorithm on Trees]]
