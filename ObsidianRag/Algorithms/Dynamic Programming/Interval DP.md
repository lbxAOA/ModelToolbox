---
category: Structural DP
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:13:24.750069+00:00
generated_by: claude
auto_generated: true
---

# Interval DP

**Parent:** [[Dynamic Programming MOC]] → Structural DP
**Tags:** #dynamic-programming #interval-dp

## Definition
DP over contiguous subarrays/substrings (intervals [i, j]), where the answer for an interval is computed by combining answers for smaller sub-intervals, typically by choosing a split point.

## Problem Recognition Signals
- "Merge adjacent elements/stones with some cost, minimize/maximize total cost" (e.g. matrix chain multiplication, stone merging).
- Palindrome partitioning/counting, optimal binary search tree, bracket matching cost problems.

## Complexity
- Time: O(n³) naive (n² intervals × O(n) split points), often optimizable to O(n²) via the quadrangle inequality / Knuth's optimization
- Space: O(n²)

## When to Use
- The problem asks to combine/merge a sequence via some binary operation where the order of combination affects total cost, over an interval structure.

## Idea
dp[i][j] = best result for the subarray/substring from i to j, computed as dp[i][k] + dp[k+1][j] + cost(i, k, j) minimized/maximized over all split points k; iterate by increasing interval length.

## Related
- [[Divide and Conquer Optimization (Quadrangle Inequality)]]
- [[Tree DP]]
