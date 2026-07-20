---
category: Number Theory
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Lucas' Theorem

**Parent:** [[Mathematics MOC]] → Number Theory
**Tags:** #mathematics #number-theory #lucas-theorem #combinatorics

## Definition
Computes C(n, k) mod p (p prime, typically small) by expressing n and k in base p and multiplying the binomial coefficients of corresponding digits: C(n,k) mod p = ∏ C(n_i, k_i) mod p.

## Problem Recognition Signals
- "Compute nCr mod p" where n, k can be up to 10^18 but p is a small prime (too small/large mismatch rules out precomputed factorials up to n).

## Complexity
- Time: O(p + log_p(n)) after O(p) precomputation of factorials mod p
- Space: O(p)

## When to Use
- n, k are far too large to precompute factorials up to n, but the prime modulus p is small enough to precompute factorials up to p.

## Idea
Write n and k in base p as digit sequences; C(n,k) mod p equals the product, over each digit position, of C(n_i, k_i) mod p (using precomputed factorials mod p for values < p), with the convention C(n_i,k_i)=0 if k_i > n_i.

## Related
- [[Permutations and Combinations]]
- [[Modular Multiplicative Inverse]]
