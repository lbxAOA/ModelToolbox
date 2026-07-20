---
category: Structural DP
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:13:24.750069+00:00
generated_by: claude
auto_generated: true
---

# Tree DP

**Parent:** [[Dynamic Programming MOC]] → Structural DP
**Tags:** #dynamic-programming #tree-dp #graph

## Definition
DP on tree-structured data where each node's DP value is computed from its children's DP values via a post-order (bottom-up) traversal.

## Problem Recognition Signals
- "Given a tree, find the maximum independent set / minimum vertex cover / diameter / optimal subtree partition."
- Any DP problem whose input is explicitly a tree (or forest) rather than a linear sequence.

## Complexity
- Time: O(n) to O(n log n) depending on whether child-state merging is O(1) amortized or requires small-to-large merging
- Space: O(n)

## When to Use
- The problem's substructure follows the tree's parent-child relationships (a subtree's answer depends only on its children's answers).

## Idea
DFS the tree in post-order; at each node, combine the DP values already computed for its children according to the recurrence (e.g. dp[v][0]/dp[v][1] for "exclude/include v" style problems), then return the combined value to the parent.

## Related
- [[Depth-First Search (DFS)]]
- [[Centroid Decomposition]]
- [[Heavy-Light Decomposition]]
