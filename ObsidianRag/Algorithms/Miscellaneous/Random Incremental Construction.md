---
category: Randomized Techniques
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:45:57.835091+00:00
generated_by: claude
auto_generated: true
---

# Random Incremental Construction

**Parent:** [[Miscellaneous MOC]] → Randomized Techniques
**Tags:** #miscellaneous #randomized #incremental-construction

## Definition
A general randomized algorithm design paradigm that inserts elements one at a time in random order, maintaining a solution incrementally, achieving good expected complexity because a random insertion order makes worst-case-triggering sequences unlikely (used e.g. in randomized minimum enclosing circle/incremental Delaunay triangulation algorithms).

## Problem Recognition Signals
- "Find the minimum enclosing circle of a point set", or other geometric construction problems with a naturally incremental structure where a fixed insertion order could be adversarial but a random one provably isn't (in expectation).

## Complexity
- Time: problem-dependent; the minimum enclosing circle is O(n) expected via this technique (Welzl's algorithm)
- Space: O(n)

## When to Use
- Geometric or combinatorial construction problems where processing elements in a fixed order risks worst-case behavior, but randomizing the order gives a provable expected-time bound.

## Idea
Shuffle the input randomly, then process elements one at a time, updating the current partial solution to account for each new element; the key insight (backward analysis) is that any element is disproportionately unlikely to force an expensive update, since it's equally likely to have appeared anywhere in the random order.

## Related
- [[Convex Hull (Monotone Chain)]]
- [[Simulated Annealing]]
