---
category: Knapsack DP
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:13:24.750069+00:00
generated_by: claude
auto_generated: true
---

# 0-1 Knapsack

**Parent:** [[Dynamic Programming MOC]] → Knapsack DP
**Tags:** #dynamic-programming #knapsack

## Definition
Given items each with a weight and value, choose a subset (each item used at most once) whose total weight fits a capacity while maximizing total value.

## Problem Recognition Signals
- "n items, each can be taken or not, capacity W, maximize value" — the defining 0/1 knapsack phrasing.
- Subset-sum / partition problems ("can you split into two equal-sum groups?") are a 0-1 knapsack special case.

## Complexity
- Time: O(n × W)
- Space: O(W) with a rolling 1D array (iterate capacity in decreasing order per item)

## When to Use
- Item selection under a single capacity constraint where each item is available once, and W is small enough for a pseudo-polynomial DP.

## Idea
dp[j] = max value achievable with capacity exactly/at-most j. For each item (w, v), update dp[j] = max(dp[j], dp[j-w] + v) iterating j from W down to w (descending order ensures each item is used at most once).

## Related
- [[Complete Knapsack]]
- [[Multiple Knapsack]]
