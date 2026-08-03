---
category: Knapsack DP
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:13:24.750069+00:00
generated_by: claude
auto_generated: true
---

# Multiple Knapsack

**Parent:** [[Dynamic Programming MOC]] → Knapsack DP
**Tags:** #dynamic-programming #knapsack

## Definition
Like 0-1 knapsack, but each item type has a limited count (between 1 and unlimited), generalizing both 0-1 and complete knapsack.

## Problem Recognition Signals
- "Item i is available in c_i copies", maximize value under capacity — explicit per-item quantity limits.

## Complexity
- Time: O(n × W × log(max count)) using binary/power-of-two splitting, or O(n × W) with a monotonic deque optimization
- Space: O(W)

## When to Use
- Bounded quantities per item type; naive expansion into individual items (treating each copy as a separate 0-1 item) is too slow for large counts.

## Idea
Binary splitting: represent c_i copies of an item as O(log c_i) "grouped" items with weights/values multiplied by powers of two (1, 2, 4, ..., remainder), then run 0-1 knapsack on the grouped items. For tighter bounds, a monotonic-queue optimization processes each remainder class of capacity mod w in O(W) total.

## Related
- [[0-1 Knapsack]]
- [[Complete Knapsack]]
- [[Monotonic Queue Optimization (DP)]]
