---
category: Spatial & Dynamic Trees
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:32:02.556432+00:00
generated_by: claude
auto_generated: true
---

# Link-Cut Tree

**Parent:** [[Data Structures MOC]] → Spatial & Dynamic Trees
**Tags:** #data-structures #link-cut-tree #dynamic-tree

## Definition
A data structure representing a forest of trees that supports link (add an edge), cut (remove an edge), and path queries (e.g. path sum, path max) all in O(log n) amortized, using splay trees to represent "preferred paths" (an application of heavy-light-decomposition ideas to a dynamically changing tree).

## Problem Recognition Signals
- "The tree/forest structure itself changes over time (edges added/removed), and path/connectivity queries must be answered between updates" — ruling out static techniques like Heavy-Light Decomposition (which assumes a fixed tree).
- "Dynamic connectivity" or "dynamic tree" explicitly mentioned in the problem.

## Complexity
- Time: O(log n) amortized per link/cut/path-query operation
- Space: O(n)

## When to Use
- The tree structure changes dynamically (edges added/removed) and path aggregate queries or connectivity checks are still needed efficiently.

## Idea
Decompose the tree into "preferred paths", each represented as a splay tree ordered by depth; an `access` operation splays a node to the root of its splay tree and re-links preferred-path splay trees along the path to the real root, after which path queries reduce to a splay-tree range query; link/cut operations manipulate these splay trees directly.

## Related
- [[Splay Tree]]
- [[Heavy-Light Decomposition]]
