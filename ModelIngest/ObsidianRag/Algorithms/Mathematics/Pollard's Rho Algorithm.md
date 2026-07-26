---
category: Number Theory
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Pollard's Rho Algorithm

**Parent:** [[Mathematics MOC]] → Number Theory
**Tags:** #mathematics #number-theory #pollards-rho #factorization

## Definition
A randomized algorithm for finding a non-trivial factor of a composite number n in roughly O(n^(1/4)) time, based on the birthday-paradox-driven collision of a pseudo-random sequence modulo n.

## Problem Recognition Signals
- "Factorize a single large number (up to 10^18)" where trial division up to sqrt(n) is too slow.

## Complexity
- Time: O(n^(1/4)) expected per factor found (often written as O(sqrt(p)) where p is the smallest prime factor)
- Space: O(1)

## When to Use
- Integer factorization of numbers too large for trial division but not so large as to need industrial-grade factoring methods (competitive programming range, up to ~10^18).

## Idea
Generate a pseudo-random sequence x_{i+1} = (x_i² + c) mod n; by the birthday paradox, two sequence values collide modulo some factor p of n well before colliding modulo n itself, so gcd(|x_i - x_j|, n) frequently reveals a non-trivial factor; Floyd's or Brent's cycle detection finds such a collision efficiently, and Miller-Rabin checks primality of resulting factors recursively.

## Related
- [[Miller-Rabin Primality Test]]
- [[GCD and Extended Euclidean Algorithm]]
