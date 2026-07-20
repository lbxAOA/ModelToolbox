---
category: Number Theory
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Bezout's Identity

**Parent:** [[Mathematics MOC]] → Number Theory
**Tags:** #mathematics #number-theory #bezout

## Definition
For integers a, b, there exist integers x, y such that a·x + b·y = gcd(a, b); more generally, the set of all integer linear combinations of a and b is exactly the set of multiples of gcd(a, b).

## Problem Recognition Signals
- "Does there exist a solution to ax + by = c?" (answer: iff gcd(a,b) divides c) — linear Diophantine equation feasibility/construction problems.

## Complexity
- Time: O(log(min(a,b))) via extended Euclid to find one solution
- Space: O(1)

## When to Use
- Determining solvability of, or explicitly solving, linear Diophantine equations ax + by = c.

## Idea
Run the extended Euclidean algorithm to get x0, y0 with a·x0 + b·y0 = g = gcd(a,b); a solution to ax+by=c exists iff g | c, given by x = x0·(c/g), y = y0·(c/g), with the general solution family x + k·(b/g), y - k·(a/g) for integer k.

## Related
- [[GCD and Extended Euclidean Algorithm]]
