---
category: Recursion & Greedy
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:03:53.991853+00:00
generated_by: claude
auto_generated: true
---

# Greedy Algorithm

**Parent:** [[Algorithm Fundamentals MOC]] → Recursion & Greedy
**Tags:** #algorithm-fundamentals #greedy

## Definition
Build up a solution by always making the locally optimal choice at each step, without reconsidering earlier decisions, relying on a proof that local optimality implies global optimality.

## Problem Recognition Signals
- "Minimize/maximize... by choosing an order/schedule of activities/intervals."
- Sorting by some key (deadline, ratio, size) then scanning once seems to work on small examples.
- No DP-like overlapping subproblems; each decision looks independent once sorted.

## Complexity
- Time: usually dominated by sorting or a priority queue, O(n log n)
- Space: O(n)

## When to Use
- The problem exhibits the greedy-choice property and optimal substructure (must be proven, e.g. via exchange argument or matroid structure).
- Common in scheduling, interval selection, Huffman coding, MST construction.

## Idea
Sort or prioritize candidates by some criterion, then scan through committing to each choice that doesn't violate constraints, never backtracking. A greedy algorithm without a correctness proof is just a heuristic — always verify with an exchange argument or counterexample search.

## Related
- [[Kruskal's Algorithm]]
- [[Prim's Algorithm]]
- [[Huffman Tree]]
