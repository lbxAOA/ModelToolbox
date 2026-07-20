---
category: Classic Puzzles & Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:45:57.835091+00:00
generated_by: claude
auto_generated: true
---

# Josephus Problem

**Parent:** [[Miscellaneous MOC]] → Classic Puzzles & Structures
**Tags:** #miscellaneous #josephus-problem

## Definition
A classic elimination problem: n people stand in a circle, and every k-th remaining person is eliminated in turn until one (or a specified number) remains; asks for the position of the survivor(s) or the elimination order.

## Problem Recognition Signals
- Explicit "people in a circle, count off and eliminate every k-th" phrasing, or any cyclic-elimination simulation problem.

## Complexity
- Time: O(n) via the recurrence-based approach (or O(k log n) for a faster variant when k is small relative to n), O(n·k) via naive simulation with a linked list/array
- Space: O(1) for the recurrence approach, O(n) for simulation

## When to Use
- Direct instances of the circular elimination problem, or as a component within a larger simulation.

## Idea
The recurrence f(n,k) = (f(n-1,k) + k) mod n (with f(1,k)=0) gives the 0-indexed survivor position for n people directly, derived by relabeling positions after each elimination; for simulating the full elimination order (not just the final survivor), use a circular linked list or a Fenwick-tree-based "find the i-th remaining element" structure for O(n log n) simulation.

## Related
- [[Linked List]]
- [[Fenwick Tree]]
