---
category: Knapsack DP
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:13:24.750069+00:00
generated_by: claude
auto_generated: true
---

# Complete Knapsack

**Parent:** [[Dynamic Programming MOC]] → Knapsack DP
**Tags:** #dynamic-programming #knapsack

## Definition
Like 0-1 knapsack, but each item type is available in unlimited quantity.

## Problem Recognition Signals
- "You may take an item any number of times" / "unlimited supply of each item type", maximize value under a capacity.
- Coin-change-style "minimum coins to make amount W" or "number of ways to make amount W" problems.

## Complexity
- Time: O(n × W)
- Space: O(W)

## When to Use
- Item selection with repetition allowed, capacity constraint small enough for pseudo-polynomial DP.

## Idea
Same recurrence as 0-1 knapsack, but iterate capacity j from w up to W in increasing order per item, allowing the same item to be reused within the same pass.

## Related
- [[0-1 Knapsack]]
- [[Multiple Knapsack]]
