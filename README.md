# ModelToolbox

ModelToolbox is a clean-room, offline-first local workbench for managing non-secret model-tooling profiles and a bounded loopback protocol router. It provides three first-party clients:

- **Desktop workbench** — Flutter for Windows, macOS, and Linux.
- **Terminal workbench** — dependency-free Node client distributed through npm as [`modeltoolbox`](https://www.npmjs.com/package/modeltoolbox).
- **CLI and local Bridge** — Python 3.11+ standard-library implementation that owns local state and runtime operations.

> **Release status:** `v0.3.0` is the first unified source release for the clean-room workbench. Native desktop distribution starts with the Flutter formats currently enabled by this repository: a Windows portable bundle, a Linux relocatable bundle, and a macOS `.app` bundle. They are application bundles—not signed platform installers—until platform-specific signing and installer packaging are configured.

## Download and run

### Windows desktop — portable bundle

Download the `ModelToolbox-windows-x64-0.3.0.zip` asset from the matching GitHub Release, extract it to a writable directory, and run:

```text
modeltoolbox_workbench.exe
```

The bundle must remain intact: the executable depends on its adjacent Flutter DLLs and data directories. Windows SmartScreen may show an unknown-publisher warning until a code-signing certificate is configured.

### Linux desktop — relocatable bundle

Download `ModelToolbox-linux-x64-0.3.0.tar.gz`, then extract and run it on a compatible x64 Linux desktop with GTK3:

```sh
tar -xzf ModelToolbox-linux-x64-0.3.0.tar.gz
cd ModelToolbox-linux-x64-0.3.0
./modeltoolbox_workbench
```

This is a relocatable Flutter bundle, not an AppImage, `.deb`, RPM, Flatpak, or Snap package.

### macOS desktop — `.app` bundle

Download `ModelToolbox-macos-universal-0.3.0.zip`, extract it, and move `modeltoolbox_workbench.app` to Applications if desired. The bundle is not yet Developer-ID signed or notarized. macOS may block it until you explicitly allow it in Privacy & Security or run it through the Finder’s **Open** workflow.

### Terminal workbench — npm

```sh
npm install -g modeltoolbox
```

The terminal client requires a local source checkout and Python executable:

```powershell
$env:MODELTOOLBOX_PYTHON = "python"
$env:MODELTOOLBOX_ROOT = "C:\ModelToolbox"
mtb-tui
```

See [tui/README.md](tui/README.md) for requirements and persistent environment-variable configuration.

### Source checkout

Clone the release tag or download the source archive from GitHub Releases. The CLI is intended to run from the checkout:

```sh
python cli/main.py version
```

> The current `v0.3.0` source release contains the complete repository source for this clean-room implementation. It deliberately does not embed Python, Node, Flutter, third-party packages, credentials, models, or external tools.

## Desktop requirements

The desktop app needs a Python executable and a local ModelToolbox source checkout because the Flutter shell starts the local Bridge. Before launching the desktop workbench, configure:

```text
MODELTOOLBOX_PYTHON=<path to Python 3.11+>
MODELTOOLBOX_ROOT=<absolute path to the ModelToolbox source checkout>
```

The Flutter desktop bundle itself is dependency-free at the Dart package layer. The bridge and all management services remain in the supplied/opened source checkout.

## Current capabilities

### Non-secret profiles

- Store reusable endpoint/model profiles without API keys or other secret values.
- Preview revision-bound configuration changes before applying them.
- The verified Claude Code adapter writes only `ANTHROPIC_BASE_URL` and `ANTHROPIC_MODEL`, creates a backup, and verifies the result.
- Cursor, VS Code, Windsurf, Codex, and generic export adapters remain inspection/export-only until independently verified.

### Local loopback router

- Binds only to `127.0.0.1`.
- Converts the bounded, text-only, non-streaming subset between Anthropic Messages and OpenAI Chat Completions.
- Does not support tools, images, documents, structured outputs, retries, failover, or credential management.
- Does not store authorization values, endpoint URLs, model names, request bodies, or response bodies.

### MCP, Skills, and marketplace foundations

- Local MCP and Skill metadata are managed through guarded local contracts.
- Local process lifetime belongs to the persistent Bridge session.
- Marketplace remains local-cache and offline-first; remote catalog refresh and third-party artifact installation are not part of this release.

## Project layout

- [cli/](cli/) — Python CLI entry point and local Bridge host.
- [flutter/](flutter/) — Flutter desktop workbench (Windows, macOS, Linux).
- [tui/](tui/) — npm-distributed terminal workbench.
- [modules/](modules/) — first-party service and protocol modules.
- [tests/](tests/) — first-party Python tests.
- [tools/](tools/) — first-party build, test, and audit tooling.
- [docs/](docs/) — specifications, architecture, and governance records.

## Development and verification

The delivery boundary permits no third-party runtime, package, build, or test dependencies in this workspace. Python 3.11+, Node.js for TUI distribution, and Flutter/Dart SDK for the desktop client are platform prerequisites.

```sh
# Python tests
python tools/test/run.py

# Audit first-party-only boundary
python tools/audit/check_zero_components.py

# TUI syntax
node --check tui/src/app.mjs
node --check tui/src/render.mjs

# Flutter desktop validation
cd flutter
flutter analyze
flutter test
```

Platform-specific release builds:

```sh
# Windows host
cd flutter && flutter build windows --release

# Linux host
cd flutter && flutter build linux --release

# macOS host with Xcode
cd flutter && flutter build macos --release
```

## Release assets and integrity

Each GitHub Release should include:

- GitHub-generated source archives for the matching `vX.Y.Z` tag;
- the native Flutter bundle(s) built for that tag;
- a `SHA256SUMS.txt` file covering uploaded native assets.

Verify an asset before running it:

```sh
sha256sum -c SHA256SUMS.txt
```

On Windows PowerShell:

```powershell
Get-FileHash .\ModelToolbox-windows-x64-0.3.0.zip -Algorithm SHA256
```

## Security and privacy

- Never put API keys, credentials, recovery codes, npm tokens, or GitHub tokens into Profile fields, configuration files committed to this repository, or issue reports.
- External configuration writes and local process operations require explicit confirmation in the supported clients.
- Review [docs/governance/originality-policy.md](docs/governance/originality-policy.md) before contributing source, assets, or dependencies.

## License

[MIT](LICENSE).
