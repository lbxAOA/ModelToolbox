---
category: Palindromes
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:17:23.702564+00:00
generated_by: claude
auto_generated: true
---

# Manacher's Algorithm

**Parent:** [[Strings MOC]] → Palindromes
**Tags:** #strings #manacher #palindrome

## Definition
Finds the longest palindromic substring centered at every position of a string in linear time, by reusing previously computed palindrome radii via mirroring within a known palindromic window.

## Problem Recognition Signals
- "Find the longest palindromic substring" or "count palindromic substrings" with string length up to 10^5-10^6, ruling out the naive O(n²) expand-around-center approach.

## Complexity
- Time: O(n)
- Space: O(n)

## When to Use
- Any problem requiring palindrome-radius information at every position of a string in linear time.

## Idea
Transform the string by inserting separators (e.g. `#`) between characters to handle even/odd-length palindromes uniformly; maintain the rightmost known palindrome's boundary [l, r] and center c, and for each new position i within that boundary, initialize its radius from its mirror position i' = 2c - i (bounded by r), then extend by direct comparison past r.

## Related
- [[Palindromic Tree (Eertree)]]
- [[Z-Function]]
