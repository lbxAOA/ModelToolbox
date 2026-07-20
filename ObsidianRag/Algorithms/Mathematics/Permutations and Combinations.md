---
category: Combinatorics
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Permutations and Combinations

**Parent:** [[Mathematics MOC]] → Combinatorics
**Tags:** #mathematics #combinatorics #permutations

## Definition
Permutations P(n,k) = n!/(n-k)! count ordered selections of k from n items; combinations C(n,k) = n!/(k!(n-k)!) count unordered selections, and satisfy Pascal's rule C(n,k) = C(n-1,k-1) + C(n-1,k).

## Problem Recognition Signals
- "How many ways to choose/arrange k items from n" — the most basic and frequent combinatorics phrasing, usually combined with "mod 10^9+7".
- Sub-problems inside larger DP/counting solutions requiring binomial coefficients.

## Complexity
- Time: O(n) to precompute factorials and inverse factorials for O(1) queries thereafter, or O(n²) to build a full Pascal's triangle
- Space: O(n)

## When to Use
- Any counting problem reducible to choosing or arranging a fixed number of items, especially as a building block inside more complex combinatorial DP.

## Idea
Precompute factorials mod p and their modular inverses once; answer C(n,k) mod p as fact[n] × inv_fact[k] × inv_fact[n-k] mod p in O(1) per query.

## Related
- [[Modular Multiplicative Inverse]]
- [[Lucas' Theorem]]
- [[Catalan Numbers]]
