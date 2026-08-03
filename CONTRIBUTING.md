# Contributing

ModelToolbox is being refactored into a terminal-first multi-package workspace with one `mtb` CLI. Keep changes small, module-scoped, and compatible with that direction.

## Repository Boundaries

- `ModelCore` owns shared infrastructure only: CLI registration, configuration, path guards, process execution, JSON output, SQLite helpers, and Git deletion protection.
- `ModelIngest` converts web/local sources into organized Markdown libraries.
- `ModelProvider` owns model API and agent runtime routing.
- `ModelOffice` owns local sandbox environments.
- `ModelMemory` owns local indexing/search context.
- `ModelMCP` owns MCP registry, scaffolds, and config exports.
- `ModelSkill` owns skill discovery and generation from Markdown libraries.
- `ModelTraining` owns self-authored training plans, distillation specs, and export flows.

Do not couple modules through direct imports except through `ModelCore` or an explicitly documented package API.

## Development Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
mtb --help
mtb doctor
```

## Safety Rules

- Do not restore missing files from GitHub history during the v2 refactor unless the project owner explicitly asks for that exact recovery.
- Do not use `git reset --hard`, `git checkout --`, or other destructive commands to clean the tree.
- Run `mtb guard git-deletions --max-deleted 5` before publishing changes.
- Do not commit secrets, virtual environments, dependency folders, model weights, or raw private documents.
- Do not add vendored GPL, AGPL, or unclear-license code to first-party modules.
- Keep generated state under `.modeltoolbox/`.

## Validation

For code changes, run the narrowest relevant check first, then a broader smoke test when practical:

```powershell
python -m compileall ModelCore ModelIngest ModelProvider ModelOffice ModelMemory ModelMCP ModelSkill ModelTraining
mtb --help
mtb doctor
```

For license-sensitive changes, run the dependency license check used by CI and update `THIRD_PARTY.md` when the boundary changes.

## Commit Style

Use Conventional Commits and keep each commit focused:

```text
feat(memory): add sqlite fts index command
fix(office): reject path traversal cwd
docs: update refactor status
chore(repo): tighten package discovery
```

## Contribution Workflow

Use the standard GitHub fork and pull request workflow. Do not push changes
directly to `main`.

### 1. Fork And Clone

Fork the repository on GitHub and clone your fork.

```powershell
git clone https://github.com/<your-username>/ModelToolbox.git
cd ModelToolbox
git remote add upstream https://github.com/<upstream-owner>/ModelToolbox.git
```

### 2. Create A Branch

Sync `main` and create a focused branch for the change.

```powershell
git fetch upstream
git switch main
git merge --ff-only upstream/main
git switch -c feat/short-description
```

### 3. Validate And Commit

Make the change, run the relevant validation, and review the diff before
committing.

```powershell
git status
git diff --check
git diff
git add <files>
git commit -m "feat(scope): short description"
```

### 4. Push And Open A Pull Request

Push the branch to your fork and open a pull request against the upstream
repository's `main` branch.

```powershell
git push --set-upstream origin feat/short-description
```

Keep the pull request focused, explain what changed and why, and include the
validation commands you ran. Link related issues with `Closes #<issue-number>`
when applicable. Address review feedback with additional commits; maintainers
may squash commits when merging.

Repository collaborators may create the branch in the upstream repository
instead of a fork, but must still submit changes through a pull request.
