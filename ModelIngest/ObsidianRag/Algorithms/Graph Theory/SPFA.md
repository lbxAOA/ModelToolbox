---
category: Shortest Path
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:35:24.462836+00:00
generated_by: claude
auto_generated: true
---

# SPFA

**Parent:** [[Graph Theory MOC]] → Shortest Path
**Tags:** #graph-theory #shortest-path #spfa

## Definition
A queue-based optimization of Bellman-Ford that only re-relaxes edges out of vertices whose distance was just improved, giving good average-case performance (though the same O(VE) worst case, and vulnerable to adversarial inputs).

## Problem Recognition Signals
- Negative edge weights present, and the graph is sparse enough / not adversarially constructed that SPFA's average-case speed beats plain Bellman-Ford.

## Complexity
- Time: O(k × E) average case for small constant k, O(V × E) worst case (can be forced by adversarial graphs, so many competitive judges specifically construct anti-SPFA tests)
- Space: O(V)

## When to Use
- Negative weights present and Bellman-Ford's guaranteed O(VE) is a practical bottleneck; be aware some contest problems are specifically designed to defeat SPFA's average case.

## Idea
Maintain a queue of vertices whose distance improved and needs propagating; pop a vertex, relax its outgoing edges, and push any neighbor whose distance improved (if not already queued); track per-vertex enqueue counts to detect negative cycles (a vertex enqueued ≥ V times indicates one).

## Related
- [[Bellman-Ford Algorithm]]
- [[Breadth-First Search (BFS)]]
