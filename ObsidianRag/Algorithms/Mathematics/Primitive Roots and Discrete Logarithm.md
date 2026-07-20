---
category: Number Theory
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Primitive Roots and Discrete Logarithm

**Parent:** [[Mathematics MOC]] → Number Theory
**Tags:** #mathematics #number-theory #primitive-root #discrete-log #bsgs

## Definition
A primitive root modulo m is an element g whose powers generate every unit modulo m; given g and a target value, the discrete logarithm problem asks for the exponent x with g^x ≡ a (mod m), typically solved by the Baby-Step Giant-Step (BSGS) meet-in-the-middle algorithm.

## Problem Recognition Signals
- "Find x such that g^x ≡ a (mod p)" — the direct discrete-log signature.
- NTT/polynomial-multiplication setup requiring a primitive root of a prime for root-of-unity computations.

## Complexity
- Time: O(sqrt(m) log m) for BSGS via a hash map of baby steps
- Space: O(sqrt(m))

## When to Use
- Solving g^x ≡ a (mod m) for x, or finding a generator/primitive root of a prime for use in NTT.

## Idea
BSGS splits x = i·sqrt(m) - j for 0 ≤ i, j < sqrt(m); precompute a hash map of g^j (baby steps) for all j, then for each i, check if a·g^(i·sqrt(m)) matches a stored g^j (giant steps), giving x = i·sqrt(m) - j.

## Related
- [[Quadratic Residues]]
- [[Fast Exponentiation]]
- [[Number Theoretic Transform (NTT)]]
