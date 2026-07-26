---
category: Number Theory
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Fermat's Little Theorem and Euler's Theorem

**Parent:** [[Mathematics MOC]] → Number Theory
**Tags:** #mathematics #number-theory #fermat #euler-theorem

## Definition
Fermat's little theorem: for prime p and a not divisible by p, a^(p-1) ≡ 1 (mod p). Euler's theorem generalizes this to any modulus m: a^φ(m) ≡ 1 (mod m) whenever gcd(a, m) = 1.

## Problem Recognition Signals
- Need a modular inverse under a prime modulus (a^(p-2) is the inverse).
- "Compute a^b mod m" where b is astronomically large (e.g. b given as another exponentiation) — reduce b modulo φ(m) (with care for the a-and-m-not-coprime edge case, which requires the generalized Euler theorem with an additive correction for small exponents).

## Complexity
- Time: O(log p) to apply via fast exponentiation
- Space: O(1)

## When to Use
- Computing modular inverses under a prime modulus, or collapsing huge exponent towers modulo φ(m).

## Idea
Fermat's little theorem falls out of Euler's theorem when m = p is prime (since φ(p) = p-1). To use for inverses: a^(p-2) mod p = a^(-1) mod p. To reduce a huge exponent tower a^b mod m, compute b mod φ(m) (adding φ(m) back if a and m share factors and b ≥ log2(m), per the generalized Euler theorem).

## Related
- [[Euler's Totient Function]]
- [[Fast Exponentiation]]
- [[Modular Multiplicative Inverse]]
