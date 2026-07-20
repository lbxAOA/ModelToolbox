---
category: Balanced Binary Search Trees
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:32:02.556432+00:00
generated_by: claude
auto_generated: true
---

# Splay Tree

**Parent:** [[Data Structures MOC]] → Balanced Binary Search Trees
**Tags:** #data-structures #splay-tree #balanced-bst

## Definition
A self-adjusting binary search tree that moves any accessed node to the root via a sequence of rotations ("splaying"), giving O(log n) amortized time per operation and the useful side effect that recently accessed elements are fast to access again.

## Problem Recognition Signals
- Need a BST supporting split/merge plus range operations (reverse a range, add to a range) on an implicit sequence — splay trees make range extraction easy (splay the range's boundary elements to the root/near-root, then the range is a contiguous subtree).
- Link-Cut Tree implementations use splay trees as their underlying "preferred path" structure.

## Complexity
- Time: O(log n) amortized per operation
- Space: O(n)

## When to Use
- Sequence maintenance with range reversal/rotation/aggregate needs, or as the building block for Link-Cut Trees.

## Idea
After accessing (finding, inserting near, etc.) a node, repeatedly apply zig/zig-zig/zig-zag rotations to move it to the root; the amortized analysis (via a potential function on subtree sizes) guarantees O(log n) amortized despite individual operations sometimes being O(n) worst case.

## Related
- [[Treap]]
- [[Link-Cut Tree]]
