---
category: Number Theory
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Mobius Function and Mobius Inversion

**Parent:** [[Mathematics MOC]] → Number Theory
**Tags:** #mathematics #number-theory #mobius-inversion

## Definition
The Mobius function μ(n) is 0 if n has a squared prime factor, else (-1)^k for k distinct prime factors; Mobius inversion lets a sum g(n) = Σ_{d|n} f(d) be inverted to recover f(n) = Σ_{d|n} μ(d)·g(n/d).

## Problem Recognition Signals
- "Count pairs (i, j) with gcd(i, j) = 1" or more generally with gcd(i,j) satisfying some condition — the classic Mobius-inversion coprime-counting signature.
- Sums over gcd values that can be rewritten via Σ_{d|gcd} μ(d) = [gcd == 1].

## Complexity
- Time: O(N) to sieve μ for all values up to N; typically O(N) or O(N log N) total for the inversion-based sum, often improved to O(sqrt(N)) per term via block/divisor enumeration
- Space: O(N)

## When to Use
- Sums or counts involving gcd conditions between pairs, or divisor-sum relationships that are easier to compute in the "summed" direction (g) than directly (f).

## Idea
Sieve μ(n) alongside primes (multiplicative function, μ(p)=-1, μ(p^k)=0 for k≥2). To count pairs with gcd exactly 1, rewrite [gcd(i,j)=1] = Σ_{d | gcd(i,j)} μ(d), swap summation order to sum over d first, and use the identity Σμ(d)·f(count of multiples of d).

## Related
- [[Linear Sieve]]
- [[Dirichlet Convolution]]
- [[Euler's Totient Function]]
