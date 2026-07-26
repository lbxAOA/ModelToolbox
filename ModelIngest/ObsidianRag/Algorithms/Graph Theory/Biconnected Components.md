---
category: Connectivity
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:35:24.462836+00:00
generated_by: claude
auto_generated: true
---

# Biconnected Components

**Parent:** [[Graph Theory MOC]] → Connectivity
**Tags:** #graph-theory #biconnected-components #block-cut-tree

## Definition
Maximal edge sets (blocks) of an undirected graph such that no single vertex removal disconnects the block internally; found via a DFS edge-stack algorithm alongside articulation point detection, and summarized structurally by a block-cut tree.

## Problem Recognition Signals
- Problems needing the block-cut tree structure to answer queries about which articulation points separate which biconnected regions, or counting simple-cycle-containing components.

## Complexity
- Time: O(V + E)
- Space: O(V + E)

## When to Use
- Beyond just identifying articulation points/bridges, when the actual grouping of edges into 2-connected blocks (and the tree structure relating blocks to cut vertices) is needed for further queries.

## Idea
During the same DFS used for articulation points, maintain a stack of edges; whenever an articulation-point condition is detected at vertex u via child v (low[v] ≥ disc[u]), pop edges off the stack down to and including edge (u,v) — the popped edges form one biconnected component. The block-cut tree then alternates block-nodes and cut-vertex-nodes based on which blocks each cut vertex belongs to.

## Related
- [[Tarjan's Bridges and Articulation Points]]
