---
category: Canonical Forms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:17:23.702564+00:00
generated_by: claude
auto_generated: true
---

# Lyndon Decomposition (Duval's Algorithm)

**Parent:** [[Strings MOC]] → Canonical Forms
**Tags:** #strings #lyndon-decomposition #duval

## Definition
Decomposes a string uniquely into a non-increasing sequence of Lyndon words (strings strictly smaller than all of their own proper suffixes/rotations) whose concatenation reconstructs the original string, computed by Duval's algorithm in linear time.

## Problem Recognition Signals
- Problems explicitly about finding the lexicographically smallest rotation of a string, or requiring a canonical decomposition into "minimal" repeating-unit-like blocks.

## Complexity
- Time: O(n)
- Space: O(1) extra beyond output

## When to Use
- Finding the smallest rotation of a string (a direct corollary of the decomposition), or any problem requiring the Lyndon factorization itself (e.g. certain string-periodicity or combinatorics-on-words problems).

## Idea
Duval's algorithm scans the string maintaining three pointers tracking a candidate Lyndon word being extended; when a comparison shows the current block would break the Lyndon property, it emits complete Lyndon words found so far and resets, achieving amortized O(n) with total work bounded by pointer advancement.

## Related
- [[Minimal String Rotation]]
