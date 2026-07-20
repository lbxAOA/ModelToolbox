---
category: Number Theory
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Linear Sieve

**Parent:** [[Mathematics MOC]] → Number Theory
**Tags:** #mathematics #number-theory #sieve #euler-sieve

## Definition
A variant of the Sieve of Eratosthenes (the Euler sieve) that finds all primes up to N in strictly O(N) time by ensuring every composite number is marked exactly once, using its smallest prime factor.

## Problem Recognition Signals
- N up to 10^8-10^9 where even the O(N log log N) sieve's constant factor is too slow.
- Need to also compute a multiplicative function (Euler's totient, Mobius function, smallest prime factor) for every number up to N simultaneously.

## Complexity
- Time: O(N)
- Space: O(N)

## When to Use
- Strict O(N) sieving is required, or a multiplicative arithmetic function needs to be tabulated for every integer up to N alongside primality.

## Idea
Iterate i from 2 to N; if i is unmarked, it's prime. For each i (prime or not), iterate over the primes found so far in increasing order, marking i·prime as composite with prime as its smallest prime factor, and stop the inner loop as soon as prime divides i (this guarantees each composite is marked exactly once, by its smallest prime factor).

## Related
- [[Sieve of Eratosthenes]]
- [[Euler's Totient Function]]
- [[Mobius Function and Mobius Inversion]]
