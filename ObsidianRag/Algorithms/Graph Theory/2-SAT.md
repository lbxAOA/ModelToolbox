---
category: Satisfiability
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:35:24.462836+00:00
generated_by: claude
auto_generated: true
---

# 2-SAT

**Parent:** [[Graph Theory MOC]] → Satisfiability
**Tags:** #graph-theory #2-sat #scc

## Definition
Decides satisfiability of a boolean formula in conjunctive normal form where every clause has exactly 2 literals, in linear time, by encoding each clause as implications in a graph and checking whether any variable and its negation end up in the same strongly connected component (which would make it unsatisfiable).

## Problem Recognition Signals
- "Each of n variables/items must be assigned one of 2 states, subject to pairwise constraints like 'if A then not B' / 'A or B must hold'" — the defining boolean-pair-constraint signature.
- Problems phrased as choosing one of two options per item with pairwise incompatibility/implication constraints.

## Complexity
- Time: O(V + E) where V, E are linear in the number of variables and clauses
- Space: O(V + E)

## When to Use
- Constraint satisfaction where each variable is binary and every constraint reduces to an implication or disjunction between two literals.

## Idea
For each variable x, create two nodes (x, ¬x); each clause (a ∨ b) becomes two implications ¬a→b and ¬b→a as directed edges; compute SCCs of this implication graph — the formula is satisfiable iff no variable's two nodes (x and ¬x) are in the same SCC, and a satisfying assignment sets each variable to whichever of x/¬x comes later in reverse-topological SCC order.

## Related
- [[Tarjan's Strongly Connected Components]]
- [[Disjoint Set Union (DSU)]]
