---
category: DP Optimizations
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:13:24.750069+00:00
generated_by: claude
auto_generated: true
---

# Convex Hull Trick (Slope Optimization)

**Parent:** [[Dynamic Programming MOC]] → DP Optimizations
**Tags:** #dynamic-programming #dp-optimization #convex-hull-trick

## Definition
Speeds up DP transitions of the form dp[i] = min/max over j of (dp[j] + b[j]·x[i] + c[j]) — i.e. each predecessor j defines a line, and the answer for i is the extreme value of all lines evaluated at x[i] — by maintaining the lower/upper convex hull of the lines.

## Problem Recognition Signals
- DP recurrence that, when rearranged algebraically, becomes "minimize over j of a linear function of i" (a slope × x[i] + intercept form) — common in cost-minimization DPs (e.g. task scheduling, print/word-wrap cost problems).
- Naive transition is O(n²) and constraints (n up to 10^5-10^6) demand O(n log n) or O(n).

## Complexity
- Time: O(n log n) general case, O(n) if slopes and queries are both monotonic (using a deque instead of a balanced structure)
- Space: O(n)

## When to Use
- The DP transition can be rewritten as evaluating a set of lines (one added per state) at a query point and taking the min/max, i.e. is a genuine "min/max of linear functions" problem.

## Idea
Maintain the lower (for min) or upper (for max) envelope of lines added so far as a convex hull; when a new line is added, pop hull lines it makes obsolete; to query at x[i], walk (or binary search) the hull to the line giving the extreme value at x[i].

## Related
- [[Li Chao Tree]]
- [[Divide and Conquer Optimization (Quadrangle Inequality)]]
