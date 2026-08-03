---
category: Balanced Binary Search Trees
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:32:02.556432+00:00
generated_by: claude
auto_generated: true
---

# Cartesian Tree

**Parent:** [[Data Structures MOC]] → Balanced Binary Search Trees
**Tags:** #data-structures #cartesian-tree

## Definition
A binary tree built from a sequence that is simultaneously a BST by array index (in-order traversal recovers the original sequence order) and a heap by value (each parent's value is ≤ or ≥ both children's), constructible from an array in O(n) via a monotonic stack.

## Problem Recognition Signals
- Building the tree underlying an O(1)-per-query RMQ-via-LCA reduction (Cartesian tree + Euler tour + sparse table gives O(n) build, O(1) query RMQ).
- Treap is exactly a Cartesian tree over (key, random priority) pairs — relevant when explaining/implementing that connection.

## Complexity
- Time: O(n) to build from an array
- Space: O(n)

## When to Use
- As the structural bridge between RMQ and LCA (RMQ ↔ LCA on Cartesian tree ↔ RMQ on Euler tour, a classic equivalence), or wherever a treap-like structure needs a deterministic (non-random) construction from existing data.

## Idea
Process the array left to right maintaining a monotonic stack of the current rightmost path of the tree; each new element pops (and becomes the new parent of) stack elements it dominates by value, then attaches as the right child of the new stack top — an O(n) amortized construction.

## Related
- [[Monotonic Stack]]
- [[Sparse Table]]
- [[Treap]]
