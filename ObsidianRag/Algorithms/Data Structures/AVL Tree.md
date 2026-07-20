---
category: Balanced Binary Search Trees
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:32:02.556432+00:00
generated_by: claude
auto_generated: true
---

# AVL Tree

**Parent:** [[Data Structures MOC]] → Balanced Binary Search Trees
**Tags:** #data-structures #avl-tree #balanced-bst

## Definition
A binary search tree that maintains the invariant that the heights of every node's two subtrees differ by at most 1, restoring this via rotations after each insert/delete, giving strict O(log n) worst-case height.

## Problem Recognition Signals
- Contexts requiring a strictly height-balanced BST with guaranteed worst-case (not amortized) O(log n) operations, e.g. as a textbook/library map implementation.

## Complexity
- Time: O(log n) worst case per insert/delete/search
- Space: O(n)

## When to Use
- Deterministic worst-case O(log n) guarantees matter more than implementation simplicity (competitive programming more often reaches for Treap/Splay for their simpler split/merge support).

## Idea
Each node tracks a balance factor (height difference of its subtrees); after an insert/delete potentially unbalances an ancestor (|balance factor| becomes 2), apply the appropriate single or double rotation (LL, RR, LR, RL cases) to restore balance, propagating checks up to the root.

## Related
- [[Red-Black Tree]]
- [[Treap]]
