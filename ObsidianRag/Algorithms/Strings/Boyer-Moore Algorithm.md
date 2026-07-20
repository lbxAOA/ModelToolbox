---
category: Exact Matching
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:17:23.702564+00:00
generated_by: claude
auto_generated: true
---

# Boyer-Moore Algorithm

**Parent:** [[Strings MOC]] → Exact Matching
**Tags:** #strings #boyer-moore #pattern-matching

## Definition
Single-pattern string matching that compares the pattern against the text right-to-left and, on a mismatch, uses precomputed "bad character" and "good suffix" heuristics to skip the pattern forward by more than one position, often skipping large chunks of the text entirely.

## Problem Recognition Signals
- Practical/real-world text search contexts (e.g. text editors, grep-like tools) rather than typical OI problems, where sublinear average-case behavior on natural language text matters.

## Complexity
- Time: O(n + m) worst case with full good-suffix table, often sublinear in practice; O(nm) naive worst case without the good-suffix rule
- Space: O(m + alphabet size)

## When to Use
- Large text, natural-language-like content, where average-case skipping gives a significant practical speedup over KMP (though KMP has simpler, tighter worst-case guarantees).

## Idea
Align the pattern at the start of the text and compare from the pattern's last character backward; on a mismatch, shift the pattern right by the maximum of the bad-character rule (align the mismatched text character with its last occurrence in the pattern) and the good-suffix rule (reuse the already-matched suffix elsewhere in the pattern).

## Related
- [[KMP Algorithm]]
