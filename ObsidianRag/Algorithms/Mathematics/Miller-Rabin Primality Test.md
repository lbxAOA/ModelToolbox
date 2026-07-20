---
category: Number Theory
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Miller-Rabin Primality Test

**Parent:** [[Mathematics MOC]] → Number Theory
**Tags:** #mathematics #number-theory #primality-test #miller-rabin

## Definition
A probabilistic (practically deterministic with fixed witness sets for numbers below known bounds) primality test that checks whether n is prime by testing several random/fixed "witness" bases against a property all primes must satisfy (derived from Fermat's little theorem plus a square-root-of-unity check).

## Problem Recognition Signals
- "Test whether a single large number (up to 10^18) is prime" — too large for trial division or a sieve.

## Complexity
- Time: O(k log³ n) for k rounds of witnesses (using fast modular multiplication)
- Space: O(1)

## When to Use
- Primality testing for individual large numbers where sieving the full range is infeasible.

## Idea
Write n-1 = d·2^s; for each witness base a, compute a^d mod n and repeatedly square up to s-1 times, checking whether the sequence ever hits 1 without having passed through -1 (n-1) — if so, n is definitely composite; using a fixed small set of witnesses (e.g. {2,3,5,7,11,13,17,19,23,29,31,37}) makes the test deterministic for all n < 3.3×10^24.

## Related
- [[Pollard's Rho Algorithm]]
- [[Fermat's Little Theorem and Euler's Theorem]]
