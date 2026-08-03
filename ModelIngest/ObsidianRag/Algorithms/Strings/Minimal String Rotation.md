---
category: Canonical Forms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:17:23.702564+00:00
generated_by: claude
auto_generated: true
---

# Minimal String Rotation

**Parent:** [[Strings MOC]] → Canonical Forms
**Tags:** #strings #minimal-rotation

## Definition
Finds the lexicographically smallest string among all cyclic rotations of a given string, in linear time.

## Problem Recognition Signals
- "Two strings are considered equal if one is a rotation of the other; canonicalize each string for comparison/hashing" — necklace/cyclic-string equivalence problems.

## Complexity
- Time: O(n)
- Space: O(n)

## When to Use
- Normalizing cyclic strings (e.g. necklaces, circular sequences) to a canonical form for equality checks, hashing, or sorting.

## Idea
Can be derived as a byproduct of Lyndon decomposition applied to the string doubled (s+s): the starting position of the last Lyndon factor beginning within the first n characters gives the rotation offset of the minimal rotation. A direct two-pointer algorithm (comparing candidate rotation starting points and advancing the losing one) achieves the same O(n) bound without an explicit Lyndon factorization.

## Related
- [[Lyndon Decomposition (Duval's Algorithm)]]
- [[String Hashing]]
