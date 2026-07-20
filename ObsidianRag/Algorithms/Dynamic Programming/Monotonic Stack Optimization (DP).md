---
category: DP Optimizations
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:13:24.750069+00:00
generated_by: claude
auto_generated: true
---

# Monotonic Stack Optimization (DP)

**Parent:** [[Dynamic Programming MOC]] → DP Optimizations
**Tags:** #dynamic-programming #dp-optimization #monotonic-stack

## Definition
Speeds up certain DP transitions by maintaining a stack of candidate states in monotonic order, popping dominated candidates so the stack always represents the Pareto-optimal set of "useful" states.

## Problem Recognition Signals
- DP where a candidate state j is never useful once a later state dominates it on every relevant metric (e.g. "largest rectangle in histogram"-style domination).
- Problems combining a monotonic-stack structural insight (nearest greater/smaller element) with a DP value carried alongside.

## Complexity
- Time: O(n) amortized, since each state is pushed and popped at most once
- Space: O(n)

## When to Use
- Each new candidate can render some previous candidates permanently useless (dominated), and "usefulness" is monotonic with respect to processing order.

## Idea
Process states left to right; before pushing the current state onto the stack, pop and discard any top-of-stack states that the current state dominates (renders strictly better/never-needed-again), then push — the stack's contents are always exactly the still-relevant candidates in monotonic order.

## Related
- [[Monotonic Stack]]
- [[Monotonic Queue Optimization (DP)]]
