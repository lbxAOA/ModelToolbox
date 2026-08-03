---
category: Hashing & Automata
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:17:23.702564+00:00
generated_by: claude
auto_generated: true
---

# String Hashing

**Parent:** [[Strings MOC]] → Hashing & Automata
**Tags:** #strings #hashing

## Definition
Map substrings to integers (typically via a polynomial rolling hash modulo a large prime) so that equality of substrings can be checked in O(1) after O(n) preprocessing, at the cost of a small false-positive probability.

## Problem Recognition Signals
- "Compare many substrings for equality", "find the longest common substring/prefix between two strings quickly", or "count distinct substrings".
- Combined with binary search: "find the longest prefix such that property X holds" using hash comparison as the O(1) check.

## Complexity
- Time: O(n) preprocessing, O(1) per substring-equality query (after computing hash from prefix hashes)
- Space: O(n)

## When to Use
- Fast substring equality/comparison is needed and an (extremely small) collision probability is acceptable; use double hashing (two different mod/base pairs) to make adversarial collisions negligible.

## Idea
Precompute prefix hashes h[i] = hash of s[0..i) using h[i] = h[i-1]·base + s[i] (mod p), plus precomputed powers of base; the hash of any substring s[l..r) is (h[r] - h[l]·base^(r-l)) mod p, computed in O(1).

## Related
- [[Suffix Array]]
- [[KMP Algorithm]]
