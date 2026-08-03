---
category: Hashing & Automata
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:17:23.702564+00:00
generated_by: claude
auto_generated: true
---

# Aho-Corasick Automaton

**Parent:** [[Strings MOC]] → Hashing & Automata
**Tags:** #strings #aho-corasick #multi-pattern-matching

## Definition
A trie of multiple patterns augmented with "failure links" (like KMP's failure function, generalized to a tree) so a text can be scanned once to find all occurrences of any of the patterns simultaneously.

## Problem Recognition Signals
- "Given a set of k patterns and a text, find all occurrences of any pattern in the text" — the defining multi-pattern-matching signature.
- Problems combining pattern matching with DP over the automaton's states (e.g. "count strings of length n avoiding all given patterns").

## Complexity
- Time: O(sum of pattern lengths) to build, O(text length + number of matches) to scan (or O(text length) if only detecting any match)
- Space: O(sum of pattern lengths × alphabet size)

## When to Use
- Matching many patterns against one (or few) texts in a single pass, or building a DP over "which patterns have been partially/fully matched so far".

## Idea
Build a trie of all patterns; then, via BFS, compute each node's failure link (pointing to the longest proper suffix of its path that's also a trie path, mirroring KMP), and augment each node with the union of matches from itself and its failure link's matches; scanning text follows trie edges, falling back via failure links on missing children.

## Related
- [[Trie]]
- [[KMP Algorithm]]
- [[Digit DP]]
