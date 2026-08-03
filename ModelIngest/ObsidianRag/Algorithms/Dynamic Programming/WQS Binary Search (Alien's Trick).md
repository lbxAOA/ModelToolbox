---
category: DP Optimizations
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:13:24.750069+00:00
generated_by: claude
auto_generated: true
---

# WQS Binary Search (Alien's Trick)

**Parent:** [[Dynamic Programming MOC]] → DP Optimizations
**Tags:** #dynamic-programming #dp-optimization #wqs-binary-search

## Definition
Removes an exact-count constraint ("choose exactly k items/segments") from a DP by binary searching on a penalty λ added to each choice's cost, turning it into an unconstrained optimization whose optimal choice count is monotonic in λ; the target k is found via binary search on λ.

## Problem Recognition Signals
- "Choose exactly k intervals/points/segments to maximize/minimize total value" where the DP over (position, count used so far) would be O(n·k) and both n and k are large.
- The unconstrained version of the problem (without the exact-k requirement) has a known convexity property in k.

## Complexity
- Time: O(n log(value range)) — an O(log) factor from binary search on λ times an O(n) unconstrained DP per iteration
- Space: O(n)

## When to Use
- f(k) = optimal value using exactly k choices is a convex (or concave) function of k, letting a penalty λ per choice be binary searched to hit exactly k choices without tracking count in the DP state.

## Idea
Binary search on penalty λ; run the DP with cost(choice) += λ (no count tracked in state) to get the unconstrained optimum and the number of choices it happens to use; adjust λ up/down based on whether that count is above/below k, until it lands on exactly k (with tie-breaking care for ties in the DP).

## Related
- [[Binary Search]]
- [[Convex Hull Trick (Slope Optimization)]]
