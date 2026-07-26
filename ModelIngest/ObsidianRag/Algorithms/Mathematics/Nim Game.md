---
category: Game Theory
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:25:56.009258+00:00
generated_by: claude
auto_generated: true
---

# Nim Game

**Parent:** [[Mathematics MOC]] → Game Theory
**Tags:** #mathematics #game-theory #nim

## Definition
A two-player impartial game with several piles of objects; players alternate removing any positive number of objects from a single pile, and the player unable to move loses (normal play). The position is losing for the player to move iff the XOR of all pile sizes is 0.

## Problem Recognition Signals
- Explicit "piles of stones" removal games, or any game phrased as "players alternately remove items, last to move wins" with independent piles/components.
- "Determine which player wins with optimal play" for a sum of independent impartial subgames.

## Complexity
- Time: O(number of piles) to XOR all pile sizes
- Space: O(1)

## When to Use
- The game is exactly Nim (piles, remove any amount from one pile), or a variant provable equivalent to Nim via the Sprague-Grundy theorem.

## Idea
Compute the XOR ("Nim-sum") of all pile sizes; if it's nonzero, the first player wins by moving to make the XOR zero (always possible), otherwise the position is a loss for the player to move under optimal opposing play.

## Related
- [[Sprague-Grundy Theorem]]
- [[Alpha-Beta Pruning]]
