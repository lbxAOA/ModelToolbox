---
category: Combinatorial Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:39:12.857299+00:00
generated_by: claude
auto_generated: true
---

# Prufer Sequence

**Parent:** [[Graph Theory MOC]] → Combinatorial Structures
**Tags:** #graph-theory #prufer-sequence #trees

## Definition
A bijection between labeled trees on n nodes and sequences of length n-2 over labels 1..n, used to count labeled trees (Cayley's formula: n^(n-2) labeled trees on n nodes) and to encode/decode trees compactly.

## Problem Recognition Signals
- "Count the number of labeled trees on n nodes (possibly with degree constraints)" — direct application of Cayley's formula or its generalization via Prufer sequences.
- "Given a Prufer sequence, reconstruct the tree" or vice versa, explicitly.

## Complexity
- Time: O(n log n) or O(n) (with a clever priority structure) to convert a tree to its Prufer sequence and back
- Space: O(n)

## When to Use
- Counting labeled trees (overall, or with prescribed degree sequences via the generalized formula), or explicit tree ↔ sequence encoding/decoding tasks.

## Idea
To build the sequence: repeatedly remove the leaf with the smallest label, appending its (former) neighbor's label to the sequence, until 2 nodes remain. To reconstruct: track each node's remaining degree (occurrences in the sequence + 1), repeatedly attach the smallest-labeled node of degree 1 to the next sequence entry, decrementing degrees, until only 2 nodes (joined by an edge) remain.

## Related
- [[Permutations and Combinations]]
