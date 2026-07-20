---
category: Constraint & Exhaustive Search
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:07:41.154989+00:00
generated_by: claude
auto_generated: true
---

# Backtracking

**Parent:** [[Search MOC]] → Constraint & Exhaustive Search
**Tags:** #search #backtracking

## Definition
Build a solution incrementally, and as soon as a partial solution can be shown to violate a constraint, abandon it ("backtrack") instead of continuing to extend it.

## Problem Recognition Signals
- "Find all/count valid configurations" satisfying constraints — N-Queens, Sudoku, permutation generation, subset generation with pruning.
- Constraint satisfaction problems where partial assignments can be checked for validity early.

## Complexity
- Time: worst-case exponential (same order as full enumeration), pruning reduces the practical constant significantly
- Space: O(depth of the decision tree)

## When to Use
- Combinatorial search (permutations, subsets, placements) where constraints can invalidate a partial solution early, making pruning effective.

## Idea
Recursively extend a partial solution by trying each next choice; check constraints immediately, and if violated, undo the choice (backtrack) and try the next option, rather than completing then checking at the end (which is plain enumeration).

## Related
- [[Enumeration]]
- [[Dancing Links (DLX)]]
- [[Recursion]]
