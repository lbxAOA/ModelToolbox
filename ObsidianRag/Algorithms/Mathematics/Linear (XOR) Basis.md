---
category: Linear Algebra
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:25:56.009258+00:00
generated_by: claude
auto_generated: true
---

# Linear (XOR) Basis

**Parent:** [[Mathematics MOC]] → Linear Algebra
**Tags:** #mathematics #linear-algebra #xor-basis #linear-basis

## Definition
A maximal linearly independent subset (over GF(2)) of a collection of integers, viewed as vectors of bits, such that every XOR-combination of the original set can be reproduced by XORing some subset of the basis, with the basis kept in reduced (each basis vector has a unique highest set bit) form.

## Problem Recognition Signals
- "Maximize/count the XOR of a subset of a given array" — the defining XOR-linear-basis signature.
- "Can value x be formed as the XOR of some subset of the given numbers?" (membership/reachability query).

## Complexity
- Time: O(n log(max value)) to build the basis from n numbers, O(log(max value)) per query (max XOR, membership test)
- Space: O(log(max value)) for the basis

## When to Use
- Any problem about which XOR values are reachable from a set of numbers, or the maximum/count of achievable XOR combinations.

## Idea
Insert each number into the basis by, from its highest set bit downward, XORing it against existing basis vectors with that leading bit until either it becomes zero (already representable, discard) or reaches an empty leading-bit slot (insert as new basis vector). To maximize XOR with the basis, greedily XOR in basis vectors from highest bit to lowest whenever doing so increases the running result.

## Related
- [[Trie]]
- [[Gaussian Elimination]]
