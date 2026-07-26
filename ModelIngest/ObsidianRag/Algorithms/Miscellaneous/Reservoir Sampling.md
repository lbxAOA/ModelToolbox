---
category: Randomized Techniques
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:45:57.835091+00:00
generated_by: claude
auto_generated: true
---

# Reservoir Sampling

**Parent:** [[Miscellaneous MOC]] → Randomized Techniques
**Tags:** #miscellaneous #reservoir-sampling #randomized

## Definition
Selects a uniformly random sample of k items from a stream of unknown or very large total length n, in a single pass, using O(k) memory.

## Problem Recognition Signals
- "Select a random element/subset from a stream where the total count isn't known in advance (or is too large to store all items)".

## Complexity
- Time: O(n) (one pass over the stream)
- Space: O(k)

## When to Use
- Uniform random sampling from a data stream where the total size is unknown upfront or too large to fit in memory all at once.

## Idea
For k=1: keep the first item as the current choice; upon seeing the i-th item, replace the current choice with it with probability 1/i (a simple inductive argument shows every item ends up with probability 1/n). For general k: keep the first k items as the initial reservoir; upon seeing the i-th item (i>k), replace a uniformly random reservoir slot with it with probability k/i.

## Related
- [[Random Incremental Construction]]
