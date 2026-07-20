---
category: Suffix Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:17:23.702564+00:00
generated_by: claude
auto_generated: true
---

# Generalized Suffix Automaton

**Parent:** [[Strings MOC]] → Suffix Structures
**Tags:** #strings #suffix-automaton #generalized-sam

## Definition
Extends the suffix automaton to represent the set of all distinct substrings across multiple strings (typically built over a trie of the input strings) instead of just one.

## Problem Recognition Signals
- "Given k strings, find substrings common to at least m of them" or "count distinct substrings across a whole collection of strings".

## Complexity
- Time: O(total length of all strings) to build
- Space: O(total length of all strings) states

## When to Use
- Multi-string substring problems where a single-string SAM isn't sufficient and building separate SAMs per string plus manual merging is more complex than building one generalized structure.

## Idea
Insert all strings into a trie first, then run the SAM-construction extend step over the trie in BFS order from the root (rather than over a single linear string), correctly handling the case where a node's extension already exists as a different trie path to avoid duplicating states.

## Related
- [[Suffix Automaton (SAM)]]
- [[Trie]]
