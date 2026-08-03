---
category: Number Theory
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Sieve of Eratosthenes

**Parent:** [[Mathematics MOC]] → Number Theory
**Tags:** #mathematics #number-theory #sieve #primes

## Definition
Finds all primes up to N by iteratively marking multiples of each found prime as composite, starting from 2.

## Problem Recognition Signals
- "Find/count all primes up to N" with N up to 10^7-10^8.
- Precomputation step before number-theory-heavy problems needing a prime list or smallest-prime-factor table.

## Complexity
- Time: O(N log log N)
- Space: O(N)

## When to Use
- Need all primes (or a primality lookup table) up to a bound N that fits in memory.

## Idea
Maintain a boolean array; for each i from 2 to N, if i is not yet marked composite, mark all multiples of i (starting from i², since smaller multiples were already marked by smaller primes) as composite.

## Related
- [[Linear Sieve]]
- [[Miller-Rabin Primality Test]]
