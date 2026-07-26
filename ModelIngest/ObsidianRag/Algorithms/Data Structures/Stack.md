---
category: Linear Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:28:58.064828+00:00
generated_by: claude
auto_generated: true
---

# Stack

**Parent:** [[Data Structures MOC]] → Linear Structures
**Tags:** #data-structures #stack

## Definition
A LIFO (last-in, first-out) collection supporting push (add to top) and pop (remove from top) in O(1).

## Problem Recognition Signals
- "Matching brackets/parentheses", expression evaluation (infix-to-postfix, calculator problems), or undo-history-style state tracking.
- Any problem naturally described via nested/recursive structure processed iteratively.

## Complexity
- Time: O(1) per push/pop/top
- Space: O(n)

## When to Use
- Nested structure matching, DFS implemented iteratively, expression parsing, or as the base for monotonic-stack techniques.

## Idea
Maintain an array or linked list where insertion/removal only happens at one end (the top); push appends, pop removes and returns the most recently added element.

## Related
- [[Queue]]
- [[Monotonic Stack]]
- [[Backtracking]]
