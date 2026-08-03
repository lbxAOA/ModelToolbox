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

ModelToolbox is distributed through npm. Install it globally on Windows,
macOS, or Linux:

```powershell
npm install -g modeltoolbox
```

Requirements:

- Node.js 18 or newer
- Python 3.11 or newer

On Windows, set `MODELTOOLBOX_PYTHON` before installation to select a specific
Python executable when needed. The package otherwise prefers the Python 3.11
launcher and falls back to `python`.

Verify the installation:

```powershell
mtb --help
mtb doctor
```

Lifecycle commands:

```powershell
mtb version
mtb doctor
npm update -g modeltoolbox
npm uninstall -g modeltoolbox
```

To pin or roll back to a release, use npm's normal version selector, for example
`npm install -g modeltoolbox@0.1.0`.

The npm package exposes the `mtb` command and runs its install bootstrap during
installation when npm install scripts are allowed. The bootstrap creates or
reuses a private `.venv` inside the installed package and installs the bundled
Python workspace. If npm install scripts are disabled, the `mtb` launcher runs
the same bootstrap on first use.

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
mtb train data dataset.jsonl --validate
mtb train recommend dataset.jsonl --gpu-memory 24GB
mtb train estimate dataset.jsonl --arch llama2-7b --method lora
mtb train plan dataset.jsonl --arch llama2-7b --output ./runs/exp1
mtb train generate-config plan.json --format huggingface
mtb train export ./runs/exp1 --format gguf
```

## ModelTraining Quick Start

Validate and plan training for small-to-medium datasets:

```powershell
# Inspect dataset
mtb train data dataset.jsonl

# Validate format and quality
mtb train data dataset.jsonl --validate

# Get architecture recommendation
mtb train recommend dataset.jsonl --gpu-memory 24GB

# Estimate resources (GPU memory, time, cost)
mtb train estimate dataset.jsonl --arch llama2-7b --method lora

# Generate training plan
mtb train plan dataset.jsonl --arch llama2-7b --output ./runs/exp1

# Generate Hugging Face or Axolotl config
mtb train generate-config plan.json --format huggingface --output config.json

# Export model after training
mtb train export ./runs/exp1 --format gguf
```

See [ModelTraining/README.md](ModelTraining/README.md) for detailed documentation.

## Refactor Status

The new MIT-owned CLI path is being built beside legacy code. Do not restore deleted files from GitHub history during this refactor. Legacy vendored training and sandbox code must be removed or isolated before the whole repository can be declared pure MIT.

## License

The first-party ModelToolbox code is intended to be MIT. Existing third-party-derived legacy directories keep their original licenses until removed or replaced. See `THIRD_PARTY.md` for the active audit.
