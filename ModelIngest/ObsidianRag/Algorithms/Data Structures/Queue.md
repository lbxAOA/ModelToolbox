---
category: Linear Structures
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:28:58.064828+00:00
generated_by: claude
auto_generated: true
---

# Queue

**Parent:** [[Data Structures MOC]] → Linear Structures
**Tags:** #data-structures #queue

## Definition
A FIFO (first-in, first-out) collection supporting enqueue (add to back) and dequeue (remove from front) in O(1) (amortized, via a circular buffer or two-stack implementation).

## Problem Recognition Signals
- BFS-based problems (shortest path in unweighted graphs, level-order traversal).
- Sliding-window / "process items in arrival order" simulation problems.

## Complexity
- Time: O(1) amortized per enqueue/dequeue
- Space: O(n)

## When to Use
- Any BFS, or maintaining strict arrival order for processing (task scheduling simulation, level-by-level traversal).

## Idea
Implement via a circular buffer with head/tail indices, or via two stacks (one for enqueue, one for dequeue, transferring when the dequeue stack empties) to get amortized O(1) with only stack primitives.

## Related
- [[Stack]]
- [[Breadth-First Search (BFS)]]
- [[Monotonic Queue]]
