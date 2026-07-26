---
category: Enumeration & Simulation
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:03:53.991853+00:00
generated_by: claude
auto_generated: true
---

# Simulation

**Parent:** [[Algorithm Fundamentals MOC]] → Enumeration & Simulation
**Tags:** #algorithm-fundamentals #simulation

## Definition
Directly model the process described by the problem step by step, rather than deriving a closed-form or clever shortcut.

## Problem Recognition Signals
- "Simulate the following process/game for q steps/days/rounds..."
- Long, procedural problem statement with many rules and special cases, small step count.
- No obvious pattern/formula; answer only makes sense by replaying the described mechanics.

## Complexity
- Time: O(number of steps × cost per step) — problem-specific
- Space: O(state size)

## When to Use
- The problem statement literally describes a process (game, automaton, physical system) to replay.
- No mathematical shortcut is obvious or the process has too many special cases to model analytically.

## Idea
Maintain the state described by the problem, apply each described transition/rule in order, and read off the answer from the final (or each intermediate) state. Correctness hinges on faithfully reproducing edge cases and off-by-one details in the statement.

## Related
- [[Enumeration]]
