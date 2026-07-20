---
category: DP Optimizations
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:13:24.750069+00:00
generated_by: claude
auto_generated: true
---

# Monotonic Queue Optimization (DP)

**Parent:** [[Dynamic Programming MOC]] → DP Optimizations
**Tags:** #dynamic-programming #dp-optimization #monotonic-queue

## Definition
Speeds up DP transitions of the form dp[i] = min/max over a sliding window of j (e.g. j in [i-k, i-1]) of (dp[j] + cost) by maintaining a monotonic deque of candidate js, so each transition is O(1) amortized instead of O(k).

## Problem Recognition Signals
- DP recurrence dp[i] = min(dp[j]) + c for j in a sliding window of fixed or variable size — explicit "window of size k" phrasing, or bounded knapsack with per-item count limits.
- Naive DP is O(n·k) and the problem hints n and k are both large (product too big for the time limit).

## Complexity
- Time: O(n) total, amortized O(1) per state
- Space: O(n) for the deque

## When to Use
- The transition range is a sliding window and the objective (min or max) needs the best value in that window, refreshed as the window slides.

## Idea
Maintain a deque of indices with monotonically increasing (for min) or decreasing (for max) dp-values; when the window slides forward, pop indices that fall out of the window from the front, and pop indices from the back that are dominated by the new candidate before pushing it, so the front of the deque is always the window's optimum.

## Related
- [[Monotonic Queue]]
- [[Multiple Knapsack]]
