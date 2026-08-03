---
category: Polynomials & Transforms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:25:56.009258+00:00
generated_by: claude
auto_generated: true
---

# Number Theoretic Transform (NTT)

**Parent:** [[Mathematics MOC]] → Polynomials & Transforms
**Tags:** #mathematics #ntt #polynomial

## Definition
An analogue of FFT performed over a finite field (modulo a prime with a suitable primitive root) instead of complex numbers, giving exact (no floating-point error) fast polynomial multiplication modulo a prime.

## Problem Recognition Signals
- "Multiply two polynomials, output coefficients modulo p" where p is a known NTT-friendly prime (e.g. 998244353), or exact integer convolution results are required (FFT's floating-point rounding is unacceptable).

## Complexity
- Time: O(n log n)
- Space: O(n)

## When to Use
- Polynomial multiplication under a modulus where exactness matters, and either the modulus is already NTT-friendly or multiple NTT-friendly primes plus CRT can reconstruct the true (unbounded) result.

## Idea
Same divide-and-conquer structure as FFT, but using a primitive n-th root of unity modulo p (found via the prime's primitive root raised to (p-1)/n) instead of complex roots of unity; all arithmetic stays in modular integers, avoiding floating-point error entirely.

## Related
- [[Fast Fourier Transform (FFT)]]
- [[Primitive Roots and Discrete Logarithm]]
- [[Chinese Remainder Theorem]]
