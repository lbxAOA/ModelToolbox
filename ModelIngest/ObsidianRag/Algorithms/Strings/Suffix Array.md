---
category: Suffix Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:17:23.702564+00:00
generated_by: claude
auto_generated: true
---

# Suffix Array

**Parent:** [[Strings MOC]] → Suffix Structures
**Tags:** #strings #suffix-array

## Definition
An array giving the starting indices of all suffixes of a string sorted lexicographically, usually paired with an LCP (longest common prefix) array giving the LCP between each pair of lexicographically adjacent suffixes.

## Problem Recognition Signals
- "Find the longest common substring between two (or more) strings", "count distinct substrings", "find the k-th lexicographically smallest substring".
- Multiple queries about substrings/suffixes ordering, repetition, or overlap on a single large string (n up to 10^5-10^6).

## Complexity
- Time: O(n log n) to build via radix-sort-based doubling, O(n) with more advanced construction (SA-IS/DC3); O(n log n) or O(n) to build the LCP array (Kasai's algorithm is O(n) given the suffix array)
- Space: O(n)

## When to Use
- Rich substring queries (ordering, repeats, common substrings) on one or more strings that a single KMP/Z-function pass can't answer directly.

## Idea
Sort all n suffixes; a common O(n log n) construction sorts suffixes by doubling the compared prefix length each round (rank pairs (rank[i], rank[i+k]) sorted via radix sort), refining ranks each round until all suffixes are distinguished. The LCP array is then built via Kasai's algorithm using the rank array's structure.

## Related
- [[Suffix Automaton (SAM)]]
- [[Sparse Table]]
- [[Radix Sort]]
