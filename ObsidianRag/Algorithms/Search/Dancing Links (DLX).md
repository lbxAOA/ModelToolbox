---
category: Constraint & Exhaustive Search
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:07:41.154989+00:00
generated_by: claude
auto_generated: true
---

# Dancing Links (DLX)

**Parent:** [[Search MOC]] → Constraint & Exhaustive Search
**Tags:** #search #dancing-links

## Definition
An efficient implementation of Knuth's Algorithm X for the Exact Cover problem, using a doubly-linked-list matrix representation that supports O(1) removal and restoration of rows/columns during backtracking.

## Problem Recognition Signals
- "Exact cover" phrasing: select a subset of rows so every column is covered exactly once.
- Sudoku solvers, pentomino/polyomino tiling, N-Queens framed as exact cover.

## Complexity
- Time: worst-case exponential (NP-hard problem), but with very low constants due to O(1) link removal/restoration
- Space: O(number of 1s in the constraint matrix)

## When to Use
- The problem can be modeled as exact cover (choose rows of a 0/1 matrix so each column has exactly one chosen row with a 1).

## Idea
Represent the constraint matrix as circular doubly-linked lists per row and column; choose the column with fewest remaining 1s, try each row covering it, "cover" (unlink) that row's columns, recurse, and "uncover" (relink) on backtrack — relinking is O(1) because removed nodes' neighbors still point to them.

## Related
- [[Backtracking]]
