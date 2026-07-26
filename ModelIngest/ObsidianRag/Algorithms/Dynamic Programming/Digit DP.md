---
category: State-Compression DP
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:13:24.750069+00:00
generated_by: claude
auto_generated: true
---

# Digit DP

**Parent:** [[Dynamic Programming MOC]] → State-Compression DP
**Tags:** #dynamic-programming #digit-dp

## Definition
DP over the digits of a number (processed most-significant to least-significant) to count/aggregate values across a numeric range, tracking whether the prefix built so far is still "tight" (bounded by the query limit) or already strictly less.

## Problem Recognition Signals
- "Count numbers in [L, R] such that ..." (digit sum, no repeated digit, specific pattern) where R can be up to 10^18.
- Phrasing explicitly about digits/decimal representation properties over a huge range.

## Complexity
- Time: O(number of digits × states per digit × 2) (the factor 2 for the tight/free flag)
- Space: O(number of digits × states per digit)

## When to Use
- Counting/summing over all integers in a range defined by their digit properties, where brute enumeration of the range is infeasible.

## Idea
Compute f(N) = count/sum for [0, N] via digit DP, then answer for [L, R] is f(R) - f(L-1). Process digits left to right with state (position, accumulated property, is_tight — whether the prefix so far equals N's prefix exactly), memoizing on non-tight states (tight states are only ever a single path so aren't memoized).

## Related
- [[Bitmask DP]]
