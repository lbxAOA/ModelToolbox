---
category: Adversarial Search
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:07:41.154989+00:00
generated_by: claude
auto_generated: true
---

# Alpha-Beta Pruning

**Parent:** [[Search MOC]] → Adversarial Search
**Tags:** #search #alpha-beta-pruning #game-theory

## Definition
An optimization of the minimax algorithm for two-player zero-sum games that prunes branches of the game tree that cannot influence the final decision, using an alpha (best guaranteed for maximizer) and beta (best guaranteed for minimizer) bound.

## Problem Recognition Signals
- Two-player turn-based games with a scorable board state (chess, tic-tac-toe-like games), asking for the optimal move or game value.
- "Both players play optimally" combined with a deep game tree that must be searched efficiently.

## Complexity
- Time: O(b^d) worst case (same as minimax), O(b^(d/2)) best case with good move ordering
- Space: O(d) for the recursion stack

## When to Use
- Deterministic, perfect-information, two-player zero-sum games where the full game tree is too large for plain minimax.

## Idea
Run minimax while tracking alpha (the maximizer's best option found so far) and beta (the minimizer's best option so far); once a node's value falls outside the [alpha, beta] window, its remaining children cannot affect the parent's decision and are skipped.

## Related
- [[Sprague-Grundy Theorem]]
- [[Nim Game]]
