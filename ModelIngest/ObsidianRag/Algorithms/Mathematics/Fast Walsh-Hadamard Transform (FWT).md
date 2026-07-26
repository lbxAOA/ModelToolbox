---
category: Polynomials & Transforms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:25:56.009258+00:00
generated_by: claude
auto_generated: true
---

# Fast Walsh-Hadamard Transform (FWT)

**Parent:** [[Mathematics MOC]] → Polynomials & Transforms
**Tags:** #mathematics #fwt #xor-convolution

## Definition
Computes convolutions defined over bitwise operators (XOR, AND, OR) instead of addition — e.g. c[k] = Σ_{i XOR j = k} a[i]·b[j] — in O(n log n) using a Hadamard-like transform, analogous to how FFT handles ordinary (addition-indexed) convolution.

## Problem Recognition Signals
- "Count pairs (i, j) such that a[i]·b[j] contributes to c[i XOR j]" or similar phrasing with AND/OR in place of XOR.
- Subset-sum-like DP over bitmask states needing a fast "subset convolution" or "XOR convolution".

## Complexity
- Time: O(n log n) where n is a power of two ≥ the value range
- Space: O(n)

## When to Use
- Convolutions indexed by a bitwise operator (XOR/AND/OR) rather than ordinary integer addition.

## Idea
Apply a transform (Hadamard transform for XOR; prefix/suffix sum transforms for OR/AND) to both sequences, multiply pointwise, then apply the corresponding inverse transform — mirroring FFT's evaluate-multiply-interpolate structure but with a different "basis" suited to the bitwise operator.

## Related
- [[Fast Fourier Transform (FFT)]]
- [[Bitmask DP]]
