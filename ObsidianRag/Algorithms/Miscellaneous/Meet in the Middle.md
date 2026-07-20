---
category: Classic Puzzles & Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:45:57.835091+00:00
generated_by: claude
auto_generated: true
---

# Meet in the Middle

**Parent:** [[Miscellaneous MOC]] → Classic Puzzles & Structures
**Tags:** #miscellaneous #meet-in-the-middle

## Definition
Splits a search space (typically 2^n subsets) into two halves, enumerates all possibilities for each half separately (2^(n/2) each), then combines results across halves (often via sorting and binary search, or a hash map), turning an O(2^n) brute force into O(2^(n/2)) or O(2^(n/2) log(2^(n/2))).

## Problem Recognition Signals
- n too large for direct 2^n enumeration (n up to ~40) but small enough that 2^(n/20) fits comfortably — "subset sum", "count subsets with a target XOR/sum" style problems with n around 30-40.

## Complexity
- Time: O(2^(n/2) × log(2^(n/2))) typical (enumeration plus sort/binary-search combination step)
- Space: O(2^(n/2))

## When to Use
- Subset-enumeration problems where n is too large for full 2^n brute force but a halved exponent (2^(n/2)) is tractable, and the two halves' results can be combined efficiently (sorted + binary search, hashing, or a two-pointer merge).

## Idea
Split the n items into two halves of size n/2; enumerate all 2^(n/2) subset results for each half independently; sort one half's results (or hash them), then for each result in the other half, binary search (or hash-lookup) for the complement/target value needed to combine into a full answer.

## Related
- [[Enumeration]]
- [[Binary Search]]
- [[Bidirectional Search]]
