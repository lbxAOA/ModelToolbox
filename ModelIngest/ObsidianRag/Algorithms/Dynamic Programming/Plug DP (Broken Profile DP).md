---
category: State-Compression DP
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:13:24.750069+00:00
generated_by: claude
auto_generated: true
---

# Plug DP (Broken Profile DP)

**Parent:** [[Dynamic Programming MOC]] → State-Compression DP
**Tags:** #dynamic-programming #plug-dp #broken-profile

## Definition
DP for tiling/connectivity problems on a grid, processed cell by cell, where the state encodes the "profile" of open connections (plugs) crossing the boundary between processed and unprocessed cells.

## Problem Recognition Signals
- Grid tiling problems (dominoes, polyominoes) or Hamiltonian-cycle-on-a-grid counting, with grid dimensions small enough that one side (e.g. width) is ≤ ~12-15.
- "Count the number of ways to tile/cover the grid such that connectivity condition X holds."

## Complexity
- Time: O(rows × cols × 2^width × transition cost), sometimes with a base-3/base-4 encoding of plug states instead of pure binary
- Space: O(2^width) or O(3^width) per row, using a rolling array

## When to Use
- Grid problems where the DP state must track connectivity across a "broken profile" boundary line sweeping through the grid, and one grid dimension is small.

## Idea
Sweep the grid cell by cell (row-major); maintain a profile of plug states along the current boundary (each plug represents whether/how a connection crosses that boundary), updating the profile at each cell based on whether it's filled and how it connects to its top/left neighbors.

## Related
- [[Bitmask DP]]
