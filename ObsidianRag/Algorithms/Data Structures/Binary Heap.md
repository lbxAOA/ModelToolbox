---
category: Heaps
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:28:58.064828+00:00
generated_by: claude
auto_generated: true
---

# Binary Heap

**Parent:** [[Data Structures MOC]] → Heaps
**Tags:** #data-structures #heap #priority-queue

## Definition
A complete binary tree (stored implicitly in an array) satisfying the heap property (each parent ≤ or ≥ both children), supporting O(log n) insert and O(log n) extract-min/max, with O(1) peek.

## Problem Recognition Signals
- "Repeatedly extract the minimum/maximum element while allowing insertions" — priority queue phrasing (Dijkstra's algorithm, Huffman coding, k-way merge, top-k streaming).

## Complexity
- Time: O(log n) insert/extract, O(1) peek, O(n) to build from an unsorted array (heapify)
- Space: O(n)

## When to Use
- Any algorithm needing repeated access to the current minimum/maximum with interleaved insertions (priority-queue-driven algorithms).

## Idea
Store the tree in an array where node i's children are at 2i+1, 2i+2; insert appends and "sifts up" (swapping with parent while violating heap order); extract swaps the root with the last element, removes the last, and "sifts down" the new root.

## Related
- [[Heap Sort]]
- [[Dijkstra's Algorithm]]
- [[Huffman Tree]]
- [[Pairing Heap]]
