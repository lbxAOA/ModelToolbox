---
category: DP Fundamentals
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:13:24.750069+00:00
generated_by: claude
auto_generated: true
---

# Memoized Search

**Parent:** [[Dynamic Programming MOC]] → DP Fundamentals
**Tags:** #dynamic-programming #memoization

## Definition
Top-down dynamic programming: a recursive function caches (memoizes) the result for each distinct set of arguments the first time it's computed, so repeated calls with the same arguments return instantly.

## Problem Recognition Signals
- A natural recursive formulation exists but the recursion tree has exponentially many repeated calls with identical arguments.
- The valid/reachable state space is sparse or irregular, making bottom-up table iteration wasteful compared to only computing states that are actually visited.

## Complexity
- Time: O(number of distinct argument tuples × cost per call)
- Space: O(number of distinct argument tuples) for the cache, plus O(depth) recursion stack

## When to Use
- The recursive structure is easiest to express top-down, or only a fraction of the full state space is actually reachable, making memoization more efficient than filling a full DP table.

## Idea
Wrap the recursive function with a cache (hash map or array) keyed by its arguments; on entry, return the cached value if present, otherwise compute, store, and return it.

## Related
- [[Recursion]]
- [[DP Fundamentals]]
