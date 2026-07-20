---
category: Suffix Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:17:23.702564+00:00
generated_by: claude
auto_generated: true
---

# Suffix Automaton (SAM)

**Parent:** [[Strings MOC]] → Suffix Structures
**Tags:** #strings #suffix-automaton #sam

## Definition
The smallest deterministic finite automaton that accepts exactly the set of suffixes of a string (equivalently, recognizes exactly the substrings of the string), built incrementally in linear time and linear size.

## Problem Recognition Signals
- "Count the number of distinct substrings", "find the longest common substring of two strings", "find the k-th lexicographically smallest distinct substring" — problems fundamentally about the set of all distinct substrings.
- Any suffix-array-solvable problem where an automaton/DAG-of-states view is more natural (e.g. combining with DP over states).

## Complexity
- Time: O(n) to build (amortized, over a constant/polynomial alphabet)
- Space: O(n) states (at most 2n-1) and O(n × alphabet size) transitions

## When to Use
- Problems about the structure of all distinct substrings of a string, especially when combined with counting (via the `endpos` size of each state) or cross-string comparison (feeding a second string through the automaton).

## Idea
Build incrementally by appending one character at a time, maintaining a "last" state; each state represents an equivalence class of substrings sharing the same set of ending positions (`endpos`), linked by suffix links forming a tree where a parent's `endpos` set is a superset of its children's.

## Related
- [[Generalized Suffix Automaton]]
- [[Suffix Array]]
- [[Palindromic Tree (Eertree)]]
