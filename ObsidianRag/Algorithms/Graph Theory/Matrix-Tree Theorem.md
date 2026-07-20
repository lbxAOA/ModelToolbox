---
category: Combinatorial Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:39:12.857299+00:00
generated_by: claude
auto_generated: true
---

# Matrix-Tree Theorem

**Parent:** [[Graph Theory MOC]] → Combinatorial Structures
**Tags:** #graph-theory #matrix-tree-theorem #kirchhoff

## Definition
Kirchhoff's theorem: the number of spanning trees of a graph equals any cofactor (or any single eigenvalue-based determinant computation) of the graph's Laplacian matrix (degree matrix minus adjacency matrix), generalizable to a weighted sum over spanning trees.

## Problem Recognition Signals
- "Count the number of spanning trees of a graph" (or the weighted sum over all spanning trees of the product of their edge weights) — direct Matrix-Tree Theorem application.

## Complexity
- Time: O(V³) to compute the determinant of the (V-1)×(V-1) reduced Laplacian via Gaussian elimination
- Space: O(V²)

## When to Use
- Counting spanning trees (or weighted spanning tree sums) of a graph, which is otherwise infeasible to enumerate directly for non-trivial graph sizes.

## Idea
Build the Laplacian matrix L = D - A (D = degree matrix, A = adjacency/weight matrix); delete any one row and the corresponding column to get the reduced Laplacian; its determinant (computed via Gaussian elimination) equals the number (or weighted sum) of spanning trees, by the Matrix-Tree Theorem.

## Related
- [[Gaussian Elimination]]
- [[Prufer Sequence]]
