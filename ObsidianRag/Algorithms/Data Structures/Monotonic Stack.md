---
category: Monotonic Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:28:58.064828+00:00
generated_by: claude
auto_generated: true
---

# Monotonic Stack

**Parent:** [[Data Structures MOC]] → Monotonic Structures
**Tags:** #data-structures #monotonic-stack

## Definition
A stack maintained in monotonically increasing or decreasing order by popping elements that violate the order before pushing a new one, used to find the nearest greater/smaller element for every position in O(n) total.

## Problem Recognition Signals
- "For each element, find the nearest element to the left/right that is greater/smaller" (next greater element).
- "Largest rectangle in a histogram", "maximum area" problems, or trapping-rain-water style problems.

## Complexity
- Time: O(n) total (each element pushed and popped at most once)
- Space: O(n)

## When to Use
- Nearest-greater/smaller-element queries for every array position, or any problem where dominated candidates can be permanently discarded.

## Idea
Scan left to right maintaining a stack in monotonic order; before pushing the current element, pop all stack elements that violate monotonicity relative to it (each popped element's "next greater/smaller" is the current element), then push.

## Related
- [[Stack]]
- [[Monotonic Queue]]
- [[Monotonic Stack Optimization (DP)]]
