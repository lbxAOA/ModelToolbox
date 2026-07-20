---
category: Combinatorics
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Pigeonhole Principle

**Parent:** [[Mathematics MOC]] → Combinatorics
**Tags:** #mathematics #combinatorics #pigeonhole-principle

## Definition
If more than n items are placed into n containers, at least one container holds more than one item; more generally, distributing N items into k containers guarantees some container holds at least ⌈N/k⌉ items.

## Problem Recognition Signals
- Existence proofs ("prove that there must exist two elements/indices such that...") rather than direct construction problems.
- Problems that reduce to bounding a search/answer size by an argument of the form "there are only k possible states, so after k+1 steps something must repeat" (common in cycle-detection and periodicity arguments).

## Complexity
- N/A — a proof/existence technique, not an algorithm with its own runtime, though it's often used to bound the complexity of an accompanying algorithm.

## When to Use
- Establishing that a solution must exist within a bounded search space, or bounding the number of steps before a repeating state guarantees a cycle (functional graphs, modular arithmetic periodicity, BSGS's meet-in-the-middle split).

## Idea
Count the number of possible "container" states or values; if the number of items/attempts exceeds that count, some collision or repetition is guaranteed, which is then exploited algorithmically (e.g. detecting a cycle once a state repeats).

## Related
- [[Primitive Roots and Discrete Logarithm]]
- [[Meet in the Middle]]
