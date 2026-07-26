---
category: Combinatorics
sources: [OI Wiki (oi-wiki.org)]
generated_at: 2026-07-06T06:21:43.807992+00:00
generated_by: claude
auto_generated: true
---

# Inclusion-Exclusion Principle

**Parent:** [[Mathematics MOC]] → Combinatorics
**Tags:** #mathematics #combinatorics #inclusion-exclusion

## Definition
Computes the size of a union of sets (or a count satisfying "none of several bad conditions") by alternately adding and subtracting the sizes of all intersections of the sets.

## Problem Recognition Signals
- "Count things avoiding ALL of several forbidden conditions" where counting each condition individually (and its overlaps) is easier than counting the target directly.
- "Count numbers divisible by none of a given small set of primes/factors", surjection/derangement-style counting.

## Complexity
- Time: O(2^k × cost per subset) for k conditions via brute subset enumeration, sometimes reducible via Mobius-style structure when conditions are divisor-based
- Space: O(1) to O(2^k)

## When to Use
- Direct counting of "satisfies none/exactly some of k conditions" is hard, but counting "satisfies at least this specific subset of conditions" is easy for every subset.

## Idea
|A1 ∪ ... ∪ Ak| = Σ|Ai| - Σ|Ai∩Aj| + Σ|Ai∩Aj∩Ak| - ...; equivalently, count(none of the conditions) = Σ_{S ⊆ conditions} (-1)^|S| × count(all conditions in S hold), summing over all subsets with alternating sign.

## Related
- [[Mobius Function and Mobius Inversion]]
- [[Derangements]]
- [[Counting DP]]
