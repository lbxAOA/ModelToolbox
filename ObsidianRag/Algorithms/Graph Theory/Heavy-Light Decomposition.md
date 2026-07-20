---
category: Tree Algorithms
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:39:12.857299+00:00
generated_by: claude
auto_generated: true
---

# Heavy-Light Decomposition

**Parent:** [[Graph Theory MOC]] → Tree Algorithms
**Tags:** #graph-theory #heavy-light-decomposition #tree #hld

## Definition
Decomposes a tree into disjoint vertical "heavy paths" (each node's edge to its largest child is "heavy") such that any root-to-node path crosses at most O(log n) distinct heavy/light path segments, enabling path queries via a linear structure (segment tree/Fenwick tree) over a flattened array.

## Problem Recognition Signals
- "Update/query the path between two nodes in a tree" (path sum, path max, path add) — the defining tree-path-query signature, on a static (non-restructuring) tree.
- "Update/query a subtree" (also solvable, more simply, since a subtree is always a contiguous range in the flattened order).

## Complexity
- Time: O(n) preprocessing, O(log² n) per path update/query (O(log n) per subtree operation)
- Space: O(n)

## When to Use
- Path or subtree updates/queries on a fixed tree structure (edges don't change) — if the tree structure itself changes dynamically, a Link-Cut Tree is needed instead.

## Idea
Compute subtree sizes via DFS; designate each node's heaviest child as its "heavy child", forming heavy chains; flatten the tree into an array ordering nodes so each heavy chain is contiguous; a path query between u and v repeatedly jumps to the top of whichever node's chain has the deeper chain-top, querying that chain segment via the underlying segment tree, until u and v are on the same chain.

## Related
- [[Segment Tree]]
- [[Link-Cut Tree]]
- [[Tree DP]]
