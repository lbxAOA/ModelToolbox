---
category: Exact Matching
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:17:23.702564+00:00
generated_by: claude
auto_generated: true
---

# KMP Algorithm

**Parent:** [[Strings MOC]] → Exact Matching
**Tags:** #strings #kmp #pattern-matching

## Definition
Finds all occurrences of a pattern in a text in linear time by precomputing a "failure function" (longest proper prefix that's also a suffix, for every prefix of the pattern) so matching never re-examines a text character after a mismatch.

## Problem Recognition Signals
- "Find all occurrences of pattern P in text T", both up to 10^5-10^6 length.
- Problems asking for the shortest period of a string or the longest border (prefix = suffix) of a string.

## Complexity
- Time: O(n + m) for text length n, pattern length m
- Space: O(m) for the failure function

## When to Use
- Single-pattern exact string matching where naive O(nm) matching is too slow.

## Idea
Build the prefix function π[i] = length of the longest proper prefix of pattern[0..i] that's also a suffix of it; while scanning the text, maintain the current match length, and on mismatch, fall back using π instead of restarting from scratch — no text character is ever re-examined.

## Related
- [[Z-Function]]
- [[Aho-Corasick Automaton]]
- [[String Hashing]]
