---
category: Polynomials & Transforms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:25:56.009258+00:00
generated_by: claude
auto_generated: true
---

# Fast Fourier Transform (FFT)

**Parent:** [[Mathematics MOC]] → Polynomials & Transforms
**Tags:** #mathematics #fft #polynomial

## Definition
Computes the Discrete Fourier Transform of a sequence (evaluating a polynomial at all n-th roots of unity, and its inverse) in O(n log n) instead of O(n²), enabling fast polynomial multiplication via evaluate-multiply-interpolate.

## Problem Recognition Signals
- "Multiply two polynomials/large integers/sequences" with degree or digit count up to 10^5-10^6, where the naive O(n²) convolution is too slow.
- Any problem reducible to a convolution: c[k] = Σ a[i]·b[k-i].

## Complexity
- Time: O(n log n) for n = next power of two ≥ combined degree
- Space: O(n)

## When to Use
- Fast polynomial/big-integer multiplication, or any convolution-shaped sum, when results can tolerate floating-point precision (or the coefficients are reconstructed as integers after rounding).

## Idea
Evaluate both polynomials at the n-th roots of unity via the recursive (or iterative, bit-reversal-based) divide-and-conquer FFT, multiply pointwise, then apply the inverse FFT to interpolate back to coefficient form.

## Related
- [[Number Theoretic Transform (NTT)]]
- [[Divide and Conquer]]
