---
category: Linear Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:28:58.064828+00:00
generated_by: claude
auto_generated: true
---

# Linked List

**Parent:** [[Data Structures MOC]] → Linear Structures
**Tags:** #data-structures #linked-list

## Definition
A sequence of nodes where each node points to the next (and, if doubly-linked, the previous), allowing O(1) insertion/removal given a node reference, at the cost of O(n) random access.

## Problem Recognition Signals
- "Insert/delete in the middle of a sequence in O(1)" given a pointer/iterator to the position, without shifting elements.
- Simulating a sequence where elements are frequently spliced/removed from arbitrary positions (e.g. Josephus-problem-style elimination).

## Complexity
- Time: O(1) insert/delete given a node reference, O(n) to reach a position by index
- Space: O(n)

## When to Use
- Frequent insertions/deletions at known positions where array shifting would be too slow, or building more complex structures (adjacency lists, LRU caches) on top.

## Idea
Each node stores its value plus pointer(s) to neighboring node(s); insertion/removal simply rewires a constant number of pointers around the target node.

## Related
- [[Josephus Problem]]
- [[Chtholly Tree]]
