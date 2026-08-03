---
category: DP Optimizations
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:13:24.750069+00:00
generated_by: claude
auto_generated: true
---

# Divide and Conquer Optimization (Quadrangle Inequality)

**Parent:** [[Dynamic Programming MOC]] → DP Optimizations
**Tags:** #dynamic-programming #dp-optimization #quadrangle-inequality

## Definition
Speeds up DP transitions of the form dp[i] = min over j<i of (dp[j] + cost(j, i)) when the optimal j for each i is monotonically non-decreasing in i (the quadrangle/Knuth-like inequality), by recursively solving for the optimal j of the middle i first and restricting the search range for the two halves.

## Problem Recognition Signals
- DP recurrence dp[i] = min_j (dp[j] + cost(j,i)) where cost satisfies the quadrangle inequality (cost(a,c)+cost(b,d) ≤ cost(a,d)+cost(b,c) for a≤b≤c≤d), often visible when the naive DP is O(n²) and problem size demands O(n log n).

## Complexity
- Time: O(n log n)
- Space: O(n)

## When to Use
- The optimal transition point is provably monotonic in i, letting divide-and-conquer restrict each recursive call's search range instead of scanning all j.

## Idea
Solve dp[mid] by brute-force scanning j only within the range known to contain the optimum (bounded by the optimal j found for the parent call's boundaries), then recurse on the left half (searching j in [lo, opt]) and right half (searching j in [opt, hi]).

## Related
- [[Interval DP]]
- [[Convex Hull Trick (Slope Optimization)]]
