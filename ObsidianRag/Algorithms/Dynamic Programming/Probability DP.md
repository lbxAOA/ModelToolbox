---
category: Counting & Probability DP
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:13:24.750069+00:00
generated_by: claude
auto_generated: true
---

# Probability DP

**Parent:** [[Dynamic Programming MOC]] → Counting & Probability DP
**Tags:** #dynamic-programming #probability-dp #expected-value

## Definition
DP where the state stores a probability or expected value, with transitions weighting predecessor states by transition probabilities and summing (linearity of expectation).

## Problem Recognition Signals
- "Compute the expected number of moves/steps/value" in a randomized process (dice games, random walks).
- "What is the probability that ..." after a sequence of random events with Markov-chain-like structure.

## Complexity
- Time: O(number of states × transitions per state)
- Space: O(number of states)

## When to Use
- The process is Markovian (next state depends only on the current state) and probabilities/expectations decompose additively or multiplicatively over states.

## Idea
Often easier to compute expectations backward from the terminal/absorbing states (E[terminal] = 0) toward the start, since forward DP on expectation can require solving a system of equations when transitions can loop back (e.g. "reroll and try again" scenarios) — in that case, set up and solve the linear equations directly, or use algebraic manipulation to remove self-loops.

## Related
- [[Counting DP]]
- [[Gaussian Elimination]]
