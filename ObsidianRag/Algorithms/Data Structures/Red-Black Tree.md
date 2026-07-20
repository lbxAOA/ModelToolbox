---
category: Balanced Binary Search Trees
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:32:02.556432+00:00
generated_by: claude
auto_generated: true
---

# Red-Black Tree

**Parent:** [[Data Structures MOC]] → Balanced Binary Search Trees
**Tags:** #data-structures #red-black-tree #balanced-bst

## Definition
A binary search tree where each node is colored red or black subject to invariants (no red node has a red child; every root-to-null path has the same number of black nodes) that together bound the tree's height at O(log n), rebalanced via rotations and recoloring.

## Problem Recognition Signals
- Rarely implemented from scratch in competitive programming (used internally by standard library ordered containers like C++'s `std::map`/`std::set`); relevant when a problem's intended solution is "just use an ordered map/set".

## Complexity
- Time: O(log n) worst case per insert/delete/search
- Space: O(n)

## When to Use
- As the (usually library-provided) backing structure for ordered associative containers; rarely hand-rolled in contest code given Treap/Splay's simpler split/merge semantics.

## Idea
Maintain the red/black coloring invariants through insertion/deletion via a case analysis of recoloring and rotations (similar in spirit to AVL but with looser, amortized-cheaper rebalancing rules, allowing up to 2x height imbalance versus AVL's tighter bound).

## Related
- [[AVL Tree]]
- [[Treap]]
