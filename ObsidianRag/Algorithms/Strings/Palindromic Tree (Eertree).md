---
category: Palindromes
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:17:23.702564+00:00
generated_by: claude
auto_generated: true
---

# Palindromic Tree (Eertree)

**Parent:** [[Strings MOC]] → Palindromes
**Tags:** #strings #palindromic-tree #eertree #palindrome

## Definition
A tree-like structure where every node represents a distinct palindromic substring of the string, built incrementally by appending one character at a time and using "suffix-palindrome links" analogous to a suffix automaton's suffix links.

## Problem Recognition Signals
- "Count the number of distinct palindromic substrings" or "for each prefix, count palindromic suffixes" — problems needing structured enumeration of all distinct palindromes, not just the longest one.

## Complexity
- Time: O(n) amortized to build (a string of length n has at most n+2 distinct palindromic substrings)
- Space: O(n)

## When to Use
- Problems requiring enumeration, counting, or DP over all distinct palindromic substrings, going beyond what Manacher's single longest-palindrome-per-center output provides.

## Idea
Maintain two roots (imaginary length -1 and length 0 palindromes); for each new character, find the longest palindromic suffix of the string-so-far via suffix-palindrome links from the previous longest palindromic suffix, and if extending it with the new character doesn't already exist as a node, create a new node linked appropriately.

## Related
- [[Manacher's Algorithm]]
- [[Suffix Automaton (SAM)]]
