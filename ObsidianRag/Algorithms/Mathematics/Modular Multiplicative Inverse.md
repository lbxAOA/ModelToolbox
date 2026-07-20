---
category: Number Theory
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Modular Multiplicative Inverse

**Parent:** [[Mathematics MOC]] → Number Theory
**Tags:** #mathematics #number-theory #modular-inverse

## Definition
The modular inverse of a modulo m is an integer x such that a·x ≡ 1 (mod m); exists iff gcd(a, m) = 1.

## Problem Recognition Signals
- "Compute nCr mod p" or any formula requiring division under a modulus ("answer modulo 10^9+7" combined with a fraction/division in the formula).

## Complexity
- Time: O(log m) via fast exponentiation (prime modulus) or extended Euclid (general modulus); O(n) to compute inverses of 1..n all at once via a linear recurrence
- Space: O(1) per value, O(n) to tabulate a range

## When to Use
- "Division" is needed inside modular arithmetic, most commonly for combinatorics formulas (factorials, binomial coefficients) modulo a prime.

## Idea
If m is prime, a^(m-2) mod m (via fast exponentiation) is the inverse by Fermat's little theorem. For general m, use the extended Euclidean algorithm to solve a·x + m·y = 1. To get inverses of 1..n all at once in O(n): inv[1]=1, inv[i] = -(m/i)·inv[m mod i] mod m.

## Related
- [[GCD and Extended Euclidean Algorithm]]
- [[Fast Exponentiation]]
- [[Fermat's Little Theorem and Euler's Theorem]]
