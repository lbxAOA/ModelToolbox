---
category: Number Theory
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Fast Exponentiation

**Parent:** [[Mathematics MOC]] → Number Theory
**Tags:** #mathematics #number-theory #fast-exponentiation

## Definition
Computes a^b (mod m) in O(log b) multiplications by repeatedly squaring the base and combining according to the binary representation of the exponent, instead of b-1 multiplications.

## Problem Recognition Signals
- "Compute a^b mod p" with b up to 10^9-10^18.
- Matrix exponentiation for linear recurrences ("compute the n-th term of a linear recurrence with n up to 10^18").

## Complexity
- Time: O(log b)
- Space: O(1) iteratively, O(log b) recursively

## When to Use
- Any modular power computation with a large exponent, or exponentiating any associative operation (matrices, polynomials) with a large power.

## Idea
Write b in binary; maintain a running result and a running "current power of a" that squares each step, multiplying it into the result whenever the corresponding bit of b is 1.

## Related
- [[Matrix Exponentiation]]
- [[Modular Multiplicative Inverse]]
