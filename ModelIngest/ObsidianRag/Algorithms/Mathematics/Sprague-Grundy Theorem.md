---
category: Game Theory
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:25:56.009258+00:00
generated_by: claude
auto_generated: true
---

# Sprague-Grundy Theorem

**Parent:** [[Mathematics MOC]] → Game Theory
**Tags:** #mathematics #game-theory #sprague-grundy #nimber

## Definition
Every impartial game position under normal play is equivalent to a Nim pile of some size, called its Grundy number (or nimber), computed as mex (minimum excludant) of the Grundy numbers of all positions reachable in one move; a sum of independent games' outcome is determined by the XOR of their Grundy numbers.

## Problem Recognition Signals
- Impartial games (both players have the same available moves from any position) that are NOT literally Nim piles but are composed of multiple independent sub-games played in parallel.
- "Two players alternately perform some game-specific move; determine the winner" where the game decomposes into independent components.

## Complexity
- Time: O(number of states × transitions per state) to compute Grundy numbers via DP/memoization, then O(number of components) to XOR them
- Space: O(number of states)

## When to Use
- An impartial game (not necessarily Nim itself) that can be decomposed into independent sub-games, where the overall winner is needed.

## Idea
Compute the Grundy number g(state) = mex{g(state') : state' reachable in one move from state} bottom-up/memoized from terminal states (g = 0); combine independent sub-games by XORing their individual Grundy numbers, then apply the same zero/nonzero rule as Nim to determine the winner.

## Related
- [[Nim Game]]
- [[Memoized Search]]
