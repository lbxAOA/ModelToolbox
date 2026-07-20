---
category: Range Query Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:28:58.064828+00:00
generated_by: claude
auto_generated: true
---

# Sparse Table

**Parent:** [[Data Structures MOC]] → Range Query Structures
**Tags:** #data-structures #sparse-table #rmq

## Definition
A precomputed table st[k][i] = the result of an idempotent, associative operation (typically min/max/gcd) over the range [i, i+2^k), enabling O(1) range queries for such operations on a static array.

## Problem Recognition Signals
- "Many range-minimum/maximum/gcd queries on a static (never-updated) array" — the Range Minimum Query (RMQ) signature.

## Complexity
- Time: O(n log n) preprocessing, O(1) per query (for idempotent operations, using overlapping ranges)
- Space: O(n log n)

## When to Use
- Static array (no updates), many range queries for an idempotent associative operation (min, max, gcd, AND, OR — not sum, which double-counts overlaps).

## Idea
Build st[k][i] = op(st[k-1][i], st[k-1][i+2^(k-1)]) bottom-up; to answer a query [l, r], pick k = floor(log2(r-l+1)) and combine the two overlapping ranges st[k][l] and st[k][r-2^k+1] (overlap is fine since the operation is idempotent).

## Related
- [[Binary Lifting]]
- [[Segment Tree]]
- [[Lowest Common Ancestor (Binary Lifting)]]
