# ModelToolbox

ModelToolbox is a terminal-first workspace for model ingestion, local memory, MCP management, skills, sandboxed execution, provider routing, and small-model training workflows.

The refactor target is one Python workspace with a single `mtb` command. Each `Model*` directory owns one bounded capability and shares only the `ModelCore` utilities for configuration, paths, process execution, JSON output, plugin loading, and SQLite state.

## Modules

- `ModelCore`: shared CLI, configuration, path guards, subprocess wrapper, JSON output, SQLite helpers, and deletion guard.
- `ModelIngest`: crawl websites, public URLs, local folders, and common file formats into organized Markdown libraries with `INDEX.md`.
- `ModelProvider`: route model and agent runtime calls across Ollama, OpenAI-compatible APIs, Anthropic, Azure OpenAI, Copilot CLI, Claude Code, Codex, and Aider.
- `ModelOffice`: local sandbox environments with venv management, bounded command execution, and workspace snapshots.
- `ModelMemory`: local SQLite FTS index for project files to reduce repeated model reads.
- `ModelMCP`: MCP server registry, discovery, scaffold generation, and config export.
- `ModelSkill`: build and manage skills from ingested Markdown libraries.
- `ModelTraining`: self-owned training planning, dataset inspection, distillation objectives, architecture presets, and export manifests.

## Install

Install the terminal app globally from this checkout:

```powershell
npm install -g .
mtb
```

The supported installation and management channels are:

- **npm, all platforms:** `npm install -g modeltoolbox` after a published release,
	or `npm install -g .` from this checkout.
- **PowerShell on Windows:** use the same npm command. Node.js 18 or newer and
	Python 3.11 or newer are required; `MODELTOOLBOX_PYTHON` can select a specific
	Python executable.
- **macOS/Linux:** use the same npm command from a shell. The bootstrap does not
	require `sudo` because the Python environment is kept inside the package
	checkout; npm itself may require the normal global-prefix permissions.
- **pipx, all platforms:** `pipx install .` from a checkout, then manage it with
	`pipx upgrade modeltoolbox` and `pipx uninstall modeltoolbox`.
- **uv, all platforms:** `uv tool install .` from a checkout, then manage it with
	`uv tool upgrade modeltoolbox` and `uv tool uninstall modeltoolbox`.

Homebrew and WinGet manifests are not published yet, so those commands are not
advertised as working installation channels. Adding either requires a released,
versioned artifact plus a formula or manifest in the external package-manager
repository.

Lifecycle commands:

```powershell
mtb version
mtb doctor
npm update -g modeltoolbox
npm uninstall -g modeltoolbox
```

## Commit And Push

The repository includes a guarded PowerShell helper. It always uses the current
branch, never creates a branch, and records commits as `lbxAOA`:

```powershell
.\scripts\commit-modeltoolbox.ps1 -Message "chore: sync refactor"
```

It stages all changes, rejects likely secrets, checks whitespace, and refuses
more than five deleted files unless the larger refactor was reviewed explicitly:

```powershell
.\scripts\commit-modeltoolbox.ps1 -Message "chore: sync refactor" -AllowLargeDeletion
```

Use `-NoPush` to create the local commit without pushing. By default the script
pushes the current `HEAD` to the existing `origin/main` branch without changing
or creating a local branch. Use `-RemoteBranch <name>` only for another branch
that already exists on `origin`; the script refuses to create remote branches.

For a checkout-based install, update and repair the editable environment with:

```powershell
npm run update
npm run bootstrap
```

To pin a published release, use npm's normal version selector, for example
`npm install -g modeltoolbox@0.1.0`. To install a local prerelease or roll back,
pass the corresponding checkout or package version to `npm install -g`.

The npm package exposes the `mtb` command and runs its install bootstrap during
installation when npm install scripts are allowed. That bootstrap creates or
reuses `.venv`, installs this Python workspace in editable mode, and then the npm
command launches the Python `mtb` control plane. If your npm policy blocks
`postinstall`, run `mtb` anyway; the launcher performs the same bootstrap on
first use when needed.

For local development, you can also run the npm-managed terminal from the
repository root:

```powershell
npm run bootstrap
npm start
```

After bootstrap, npm can also forward any `mtb` command:

```powershell
npm run mtb -- doctor
npm run mtb -- provider list --json
```

Python-only install is still supported:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

Then run:

```powershell
mtb
mtb --help
mtb doctor
```

`mtb` self-bootstraps the local `.venv` on first use if npm lifecycle scripts
were disabled. `mtb doctor` is the first troubleshooting command; it reports
the Python runtime, current directory, and installed package version without
printing credentials or environment values.

Running bare `mtb` opens the interactive ModelToolbox terminal. Type `help` to
see commands and `exit` to quit.

## Security And Local State

Obsidian's Local REST API state is machine-local and is intentionally ignored by
Git. Never commit its `data.json`, API keys, certificates, or private keys. If
credentials from an earlier checkout were exposed, revoke and regenerate the
API key and recreate the TLS certificate/private key pair in Obsidian; deleting
the local file does not invalidate credentials that were already issued.

## Command Overview

```powershell
mtb guard git-deletions --max-deleted 5
mtb ingest build --source docs --output vault/docs
mtb memory index . --include .py
mtb memory search "provider routing"
mtb provider list --json
mtb provider runtime list --json
mtb office env create demo
mtb office exec demo python -c "print('ok')"
mtb skill build-from vault/docs --name docs-skill
mtb mcp discover
mtb mcp export
mtb train data dataset.jsonl
mtb train plan dataset.jsonl --arch tiny-decoder
```

## Refactor Status

The new MIT-owned CLI path is being built beside legacy code. Do not restore deleted files from GitHub history during this refactor. Legacy vendored training and sandbox code must be removed or isolated before the whole repository can be declared pure MIT.

## License

The first-party ModelToolbox code is intended to be MIT. Existing third-party-derived legacy directories keep their original licenses until removed or replaced. See `THIRD_PARTY.md` for the active audit.
