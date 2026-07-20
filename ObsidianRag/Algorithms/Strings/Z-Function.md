---
category: Exact Matching
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:17:23.702564+00:00
generated_by: claude
auto_generated: true
---

# Z-Function

**Parent:** [[Strings MOC]] → Exact Matching
**Tags:** #strings #z-function #pattern-matching

## Definition
For a string s, computes z[i] = the length of the longest common prefix between s and the suffix of s starting at i, for every position i, in linear time (also called Extended KMP).

## Problem Recognition Signals
- Pattern matching phrased as "concatenate pattern + separator + text, then find where z[i] equals the pattern length."
- Problems about longest common prefixes between all suffixes and the whole string, or counting distinct substrings/periods.

## Complexity
- Time: O(n)
- Space: O(n)

## When to Use
- Equivalent use cases to KMP (single-pattern matching) but the Z-array formulation is often more convenient for problems directly about prefix-suffix overlaps.

## Idea
Maintain a window [l, r] = the rightmost matched z-box found so far; for each new i, if i is inside the window, initialize z[i] from the mirrored position s[i-l] (bounded by the window's remaining length) to skip redundant comparisons, then extend by direct comparison past the window.

## Related
- [[KMP Algorithm]]
- [[Suffix Array]]
