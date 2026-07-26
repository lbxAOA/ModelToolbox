---
category: Balanced Binary Search Trees
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:32:02.556432+00:00
generated_by: claude
auto_generated: true
---

# Scapegoat Tree

**Parent:** [[Data Structures MOC]] → Balanced Binary Search Trees
**Tags:** #data-structures #scapegoat-tree #balanced-bst

## Definition
A binary search tree that stays approximately balanced not through per-operation rotations but by periodically rebuilding an unbalanced subtree from scratch (into a perfectly balanced one) whenever an insertion causes some ancestor to become too unbalanced (the "scapegoat").

## Problem Recognition Signals
- Contexts wanting a balanced BST without implementing rotation logic at all, trading rotation complexity for an amortized full-subtree-rebuild approach.

## Complexity
- Time: O(log n) amortized per insert/delete, O(n) worst case for an individual rebuild (but rare/amortized away)
- Space: O(n)

## When to Use
- A simple-to-implement balanced BST is wanted and amortized (rather than worst-case-per-operation) guarantees are acceptable.

## Idea
Track subtree sizes; after inserting, walk up from the new node checking whether any ancestor's two children's sizes are too imbalanced (violates the α-weight-balance criterion) — if so, rebuild that entire ancestor's subtree into a perfectly balanced BST via an O(subtree size) in-order flatten-and-rebuild.

## Related
- [[AVL Tree]]
- [[Treap]]
