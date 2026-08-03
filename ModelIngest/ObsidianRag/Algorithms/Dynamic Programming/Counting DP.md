---
category: Counting & Probability DP
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:13:24.750069+00:00
generated_by: claude
auto_generated: true
---

# Counting DP

**Parent:** [[Dynamic Programming MOC]] → Counting & Probability DP
**Tags:** #dynamic-programming #counting-dp

## Definition
DP where the value stored per state is a count of ways (often modulo a prime) rather than a min/max optimum, with transitions summing contributions from predecessor states instead of taking a min/max.

## Problem Recognition Signals
- "Count the number of ways to ..." / "how many distinct sequences/paths/arrangements satisfy ...", frequently "output the answer modulo 10^9+7".

## Complexity
- Time: O(number of states × transition cost)
- Space: O(number of states)

## When to Use
- The problem asks for a count (not an optimum) over a space with optimal-substructure-like decomposition, and double counting must be avoided by careful state design.

## Idea
Same state/transition design process as standard DP, but each transition adds (dp[predecessor] × ways-to-transition) into dp[state] rather than taking a max/min; take all arithmetic modulo the required prime to avoid overflow.

## Related
- [[DP Fundamentals]]
- [[Probability DP]]
- [[Inclusion-Exclusion Principle]]
