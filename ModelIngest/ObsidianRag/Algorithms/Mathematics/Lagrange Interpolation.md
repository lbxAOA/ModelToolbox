---
category: Polynomials & Transforms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:25:56.009258+00:00
generated_by: claude
auto_generated: true
---

# Lagrange Interpolation

**Parent:** [[Mathematics MOC]] → Polynomials & Transforms
**Tags:** #mathematics #lagrange-interpolation #polynomial

## Definition
Reconstructs the unique degree-≤(n-1) polynomial passing through n given points, and evaluates it at any target x, without ever forming the polynomial's coefficients explicitly.

## Problem Recognition Signals
- "The answer as a function of n is a polynomial of degree ≤ k; given the answer for the first k+1 values of n, find the answer for a much larger n."
- Sum-of-powers formulas (Σ i^k) or DP outputs known to be polynomial in n but with n far too large to compute directly.

## Complexity
- Time: O(n²) general-case interpolation at one point, O(n) when the sample x-values are consecutive integers (using prefix/suffix product tricks)
- Space: O(n)

## When to Use
- The target function is known (or provable) to be a polynomial of bounded degree in some variable, and it's cheaper to brute-force compute several sample points than to derive/evaluate the closed form directly.

## Idea
Given points (x_i, y_i), the value at target x is Σ_i y_i × ∏_{j≠i} (x - x_j)/(x_i - x_j); when x_i = 0, 1, ..., n are consecutive, prefix and suffix products of (x - x_j) let each term be evaluated in O(1) amortized, giving O(n) total.

## Related
- [[Fast Fourier Transform (FFT)]]
- [[DP Fundamentals]]
