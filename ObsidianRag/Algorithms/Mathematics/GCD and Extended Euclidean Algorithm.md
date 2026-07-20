---
category: Number Theory
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# GCD and Extended Euclidean Algorithm

**Parent:** [[Mathematics MOC]] → Number Theory
**Tags:** #mathematics #number-theory #gcd

## Definition
The Euclidean algorithm computes gcd(a, b) via repeated remainder reduction (gcd(a,b) = gcd(b, a mod b)); the extended version additionally finds integers x, y such that a·x + b·y = gcd(a, b).

## Problem Recognition Signals
- "Find integers x, y such that ax + by = c" (linear Diophantine equations).
- Need a modular inverse when the modulus isn't prime (inverse via extended Euclid rather than Fermat's little theorem).

## Complexity
- Time: O(log(min(a, b)))
- Space: O(log(min(a,b))) recursion depth (O(1) iteratively)

## When to Use
- Computing GCD/LCM, solving linear Diophantine equations, or finding modular inverses with a general (not necessarily prime) modulus.

## Idea
Recursively reduce gcd(a, b) to gcd(b, a mod b) until b = 0. The extended version tracks coefficients backward through the recursion: given (x1, y1) solving b·x1 + (a mod b)·y1 = g, derive (x, y) solving a·x + b·y = g via x = y1, y = x1 - (a/b)·y1.

## Related
- [[Bezout's Identity]]
- [[Chinese Remainder Theorem]]
- [[Modular Multiplicative Inverse]]
