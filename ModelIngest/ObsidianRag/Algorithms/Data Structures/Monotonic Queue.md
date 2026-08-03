---
category: Monotonic Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:28:58.064828+00:00
generated_by: claude
auto_generated: true
---

# Monotonic Queue

**Parent:** [[Data Structures MOC]] → Monotonic Structures
**Tags:** #data-structures #monotonic-queue

## Definition
A double-ended queue (deque) maintained in monotonic order that supports finding the minimum/maximum of a sliding window in O(1) amortized per slide.

## Problem Recognition Signals
- "Find the minimum/maximum in every sliding window of size k" — the defining signature.
- DP transitions over a fixed-size or variable sliding window (see Monotonic Queue Optimization).

## Complexity
- Time: O(n) total
- Space: O(k) or O(n)

## When to Use
- Sliding-window min/max queries, or DP recurrences with a sliding-window-shaped dependency.

## Idea
Maintain a deque of indices in increasing order of value (for min) or decreasing (for max); when the window advances, pop expired indices from the front and pop dominated indices from the back before pushing the new index — the front always holds the current window's optimum.

## Related
- [[Monotonic Stack]]
- [[Monotonic Queue Optimization (DP)]]
