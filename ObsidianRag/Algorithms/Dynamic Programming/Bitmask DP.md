---
category: State-Compression DP
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:13:24.750069+00:00
generated_by: claude
auto_generated: true
---

# Bitmask DP

**Parent:** [[Dynamic Programming MOC]] → State-Compression DP
**Tags:** #dynamic-programming #bitmask-dp

## Definition
DP where part of the state (typically "which of a small set of items has been used/visited") is encoded as a bitmask integer, enabling O(1) checks/updates via bitwise operations.

## Problem Recognition Signals
- Small n (n ≤ ~20) combined with phrasing like "visit every city exactly once" (TSP), "assign each of n items to n slots", or "subset of a small set with some property".

## Complexity
- Time: O(2^n × n) or O(2^n × n²) typical for TSP-style problems
- Space: O(2^n × n)

## When to Use
- n is small enough (usually ≤ 20-24) that 2^n states are tractable, and the state needs to track a subset of used/visited elements.

## Idea
dp[mask][i] = best value when the subset of used elements is `mask` and the current position/last element is i; transition by trying to add an unused element j (mask without bit j set) via `mask | (1<<j)`.

## Related
- [[Digit DP]]
- [[Plug DP (Broken Profile DP)]]
