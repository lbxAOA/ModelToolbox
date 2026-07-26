# Third-Party Audit

This file tracks license boundaries during the v2 refactor. The target state is first-party MIT code plus normal runtime dependencies with compatible notices.

## Current Decisions

- Do not restore missing files or directories from GitHub history.
- Do not vendor AGPL, GPL, or Apache-derived application code into the first-party MIT implementation.
- Apache, BSD, and MIT pip dependencies are allowed as runtime dependencies unless a stricter policy is chosen later.
- GPL and AGPL dependencies are blocked by CI unless explicitly moved to an out-of-process optional integration.

## Known Legacy Areas

- `ModelTraining`: contains legacy unsloth-derived material and AGPL-oriented tests. The new `modeltoolbox_training` package is the self-owned replacement path.
- `ModelOffice`: contains legacy e2b-derived TypeScript/Python workspace material. The new `modeltoolbox_office` package is the local sandbox replacement path.
- `ModelMemory/code_review_graph`: source/license origin still needs final confirmation before reuse. The new `modeltoolbox_memory` package avoids importing it.
- `ObsidianRag`: content licensing should remain separate from code licensing and may need to move to runtime data.

## Required Before Pure MIT Root License

- Remove or isolate vendored AGPL/GPL/Apache application code.
- Keep generated data and knowledge vault content under explicit content licenses or outside the code repository.
- Run dependency license checks in CI.
