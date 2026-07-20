---
category: Balanced Binary Search Trees
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:32:02.556432+00:00
generated_by: claude
auto_generated: true
---

# Treap

**Parent:** [[Data Structures MOC]] → Balanced Binary Search Trees
**Tags:** #data-structures #treap #balanced-bst

## Definition
A binary search tree ordered by key, additionally assigned a random "priority" per node and kept heap-ordered by priority, so the random priorities keep the tree balanced in expectation without explicit rebalancing rules.

## Problem Recognition Signals
- "Maintain a dynamic sorted sequence supporting insert/delete/k-th-element/rank queries" where a simpler structure (Fenwick tree over ranks) doesn't fit because keys aren't from a small fixed range, or split/merge-by-key operations are needed.
- Problems needing an ordered structure that also supports split/merge (implicit treap over sequence position for range reversal/rotation).

## Complexity
- Time: O(log n) expected per insert/delete/split/merge/query
- Space: O(n)

## When to Use
- Need a balanced BST with relatively simple implementation, especially when split/merge by key or by position (implicit treap) is required.

## Idea
Insert as in a normal BST by key, then rotate the new node up while its priority violates the heap property with its parent (or implement via a simpler split/merge: split a treap into ≤k and >k parts by key, merge two treaps where all keys of one are less than the other, and express insert/delete as split+merge).

## Related
- [[Splay Tree]]
- [[Persistent Segment Tree]]
