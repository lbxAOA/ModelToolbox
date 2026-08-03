---
category: Number Theory
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Chinese Remainder Theorem

**Parent:** [[Mathematics MOC]] → Number Theory
**Tags:** #mathematics #number-theory #crt

## Definition
Given a system of congruences x ≡ a_i (mod m_i) with pairwise coprime moduli, CRT reconstructs a unique solution x modulo the product of all m_i.

## Problem Recognition Signals
- "Find x such that x mod m1 = a1, x mod m2 = a2, ..." with pairwise coprime m_i.
- Splitting a computation modulo a large composite number into computations modulo its coprime prime-power factors, then recombining.

## Complexity
- Time: O(k log M) for k congruences with product of moduli M (dominated by modular inverse computations)
- Space: O(k)

## When to Use
- Combining independent modular constraints into one, or (with NTT) multiplying polynomials modulo a non-NTT-friendly prime by working modulo several NTT-friendly primes and recombining via CRT.

## Idea
Combine congruences pairwise: given x ≡ a1 (mod m1) and x ≡ a2 (mod m2), find x ≡ a1 + m1·t (mod m1·m2) by solving for t via the modular inverse of m1 modulo m2; repeat, folding in one congruence at a time.

## Related
- [[Extended Chinese Remainder Theorem]]
- [[GCD and Extended Euclidean Algorithm]]
- [[Number Theoretic Transform (NTT)]]
