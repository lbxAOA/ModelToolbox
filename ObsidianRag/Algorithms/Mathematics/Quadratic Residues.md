---
category: Number Theory
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Quadratic Residues

**Parent:** [[Mathematics MOC]] → Number Theory
**Tags:** #mathematics #number-theory #quadratic-residues

## Definition
An integer a is a quadratic residue modulo p if there exists x with x² ≡ a (mod p); determined via Euler's criterion (a is a QR iff a^((p-1)/2) ≡ 1 mod p for odd prime p), and square roots mod p can be extracted via the Tonelli-Shanks algorithm.

## Problem Recognition Signals
- "Find x such that x² ≡ a (mod p)" or "determine whether a has a square root modulo p".

## Complexity
- Time: O(log p) to test via Euler's criterion, O(log² p) for Tonelli-Shanks to extract a square root
- Space: O(1)

## When to Use
- Solving modular square-root problems or quadratic congruences modulo a prime.

## Idea
Euler's criterion classifies a via fast exponentiation. Tonelli-Shanks factors p-1 = Q·2^S, finds a quadratic non-residue to bootstrap, and iteratively refines a candidate square root by adjusting with powers of the non-residue until it matches a exactly.

## Related
- [[Fast Exponentiation]]
- [[Primitive Roots and Discrete Logarithm]]
