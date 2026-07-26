---
category: Matching
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:39:12.857299+00:00
generated_by: claude
auto_generated: true
---

# Gale-Shapley Stable Matching

**Parent:** [[Graph Theory MOC]] → Matching
**Tags:** #graph-theory #matching #stable-matching #gale-shapley

## Definition
Given two groups each ranking members of the other group by preference, finds a matching where no unmatched pair would both prefer each other over their assigned partners (a "stable" matching), always achievable via the deferred-acceptance algorithm.

## Problem Recognition Signals
- "Each side has ranked preferences over the other side; find a matching with no pair that would both rather be matched to each other" — the defining stable-matching (stable marriage) signature.

## Complexity
- Time: O(n²) for n on each side
- Space: O(n²) to store preference lists/rankings

## When to Use
- Two-sided matching problems where stability (no incentive for any pair to defect from the matching) is the objective, not necessarily a matching optimal by some global cost.

## Idea
Each unmatched proposer proposes to their most-preferred remaining option on the other side; each receiver tentatively accepts the best proposal received so far (rejecting/replacing worse ones), and rejected proposers move to their next preference — repeat until everyone is matched; the result is always stable and is optimal for the proposing side.

## Related
- [[Hungarian Algorithm]]
