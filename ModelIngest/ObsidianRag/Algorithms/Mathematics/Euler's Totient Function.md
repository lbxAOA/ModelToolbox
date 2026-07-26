---
category: Number Theory
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Euler's Totient Function

**Parent:** [[Mathematics MOC]] → Number Theory
**Tags:** #mathematics #number-theory #euler-totient

## Definition
φ(n) counts the integers in [1, n] that are coprime to n; computed from n's prime factorization as n × ∏(1 - 1/p) over each distinct prime p dividing n.

## Problem Recognition Signals
- "Count numbers ≤ n coprime to n", or problems involving Euler's theorem (a^φ(n) ≡ 1 mod n for gcd(a,n)=1) to reduce huge exponents modulo φ(n).
- Sum-over-divisors / multiplicative-function problems referencing coprimality counts.

## Complexity
- Time: O(sqrt(n)) for a single value via trial-division factorization, O(N log log N) or O(N) to tabulate φ for all values up to N via a sieve
- Space: O(1) for a single value, O(N) for a table

## When to Use
- Coprimality counting, reducing exponents modulo φ(n) via Euler's theorem, or as a building block in Mobius-inversion-style sums.

## Idea
Factorize n into distinct primes p1, ..., pk; then φ(n) = n × (1 - 1/p1) × ... × (1 - 1/pk). φ is multiplicative, so it can be tabulated for all n up to N in a linear sieve alongside smallest-prime-factor computation.

## Related
- [[Linear Sieve]]
- [[Fermat's Little Theorem and Euler's Theorem]]
- [[Mobius Function and Mobius Inversion]]
