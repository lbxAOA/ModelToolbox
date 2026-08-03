---
category: Number Theory
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Extended Chinese Remainder Theorem

**Parent:** [[Mathematics MOC]] → Number Theory
**Tags:** #mathematics #number-theory #excrt

## Definition
Generalizes CRT to systems of congruences x ≡ a_i (mod m_i) whose moduli are not necessarily pairwise coprime, merging them pairwise using the extended Euclidean algorithm and failing only when the congruences are genuinely inconsistent.

## Problem Recognition Signals
- CRT-style system of congruences where the moduli share common factors (explicitly not guaranteed coprime).

## Complexity
- Time: O(k log M) for k congruences
- Space: O(k)

## When to Use
- Same setting as CRT but moduli are not pairwise coprime, so the standard product-based combination formula doesn't directly apply.

## Idea
Merge two congruences x ≡ a1 (mod m1), x ≡ a2 (mod m2) by solving m1·p - m2·q = a2 - a1 via extended Euclid; a solution exists iff gcd(m1, m2) divides (a2 - a1), and the merged congruence has modulus lcm(m1, m2). Fold congruences in one at a time, failing immediately if any pair is inconsistent.

## Related
- [[Chinese Remainder Theorem]]
- [[GCD and Extended Euclidean Algorithm]]
