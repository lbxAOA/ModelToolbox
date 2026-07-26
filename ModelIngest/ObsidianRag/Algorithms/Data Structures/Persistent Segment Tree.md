---
category: Persistent Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:32:02.556432+00:00
generated_by: claude
auto_generated: true
---

# Persistent Segment Tree

**Parent:** [[Data Structures MOC]] → Persistent Structures
**Tags:** #data-structures #persistent-segment-tree #segment-tree

## Definition
A segment tree variant where every update creates a new version of the tree that shares all unmodified nodes with previous versions (path-copying), letting queries against any historical version be answered without storing full copies of the array.

## Problem Recognition Signals
- "Answer queries about the array as it was after the k-th update" (versioned/historical queries).
- "Find the k-th smallest value in range [l, r]" via persistent segment trees over value-ranks (a very common competitive-programming pattern).

## Complexity
- Time: O(log n) per update (creating a new version) or query
- Space: O(n + m log n) total for n initial elements and m updates (each update only creates O(log n) new nodes)

## When to Use
- Version history needs to be queryable (not just the latest state), or the classic "k-th smallest in range" pattern via persistent structures over sorted value ranks.

## Idea
On update, instead of modifying nodes in place, create new copies only for the O(log n) nodes on the path from root to the changed leaf, having each new node's untouched child pointer point to the old (shared) subtree; each version is identified by its own root pointer into this shared structure.

## Related
- [[Segment Tree]]
- [[Persistent Trie]]
