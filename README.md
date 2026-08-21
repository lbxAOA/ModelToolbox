# ModelToolbox

ModelToolbox Next is an isolated, clean-room implementation workspace for the next self-developed ModelToolbox release.

## Delivery boundary

Only content under this directory is eligible for future delivery. It must contain no third-party source code, libraries, static assets, model weights, datasets, build tools, or test frameworks. Python 3.11+ and its standard library are supported platform prerequisites. Flutter/Dart SDK and its SDK-owned `flutter` and `flutter_test` libraries are additionally approved platform prerequisites for the `flutter/` desktop presentation client; no non-SDK pub package is allowed. Node.js and npm are approved only for the dependency-free `tui/` terminal package and its artifact transport; neither may install, download, or resolve dependencies. The operating system and hardware drivers remain external platform prerequisites.

GitHub remains source and release hosting, npm remains the distribution channel for the terminal client, and GitHub Releases host native Flutter installers. Neither GitHub Actions nor third-party build, test, packaging, or runtime dependencies belong to this workspace.

## Local profile and router configuration

ModelToolbox provides an independently implemented, CC-switch-inspired local configuration workflow. It stores reusable **non-secret** endpoint/model profiles, can preview and safely apply explicitly allowlisted configuration fields to supported local applications, and can optionally route a small compatible request subset through a loopback listener.

- Profiles store an endpoint, optional model, adapter identity, and optional credential-source *name*. API keys and other secret values are never read, stored, displayed, or written.
- Only the verified Claude Code adapter can modify settings. It previews a content-revision-bound diff, writes only `ANTHROPIC_BASE_URL` and `ANTHROPIC_MODEL`, creates a backup, and verifies the result. Other adapter identities remain visible but disabled until their contracts are verified.
- Router policy changes are previewed and revision-bound. The TUI and Flutter client can start/stop a listener owned by their persistent local bridge session; it stops with that bridge. For headless use, run `router-serve` in a separately supervised foreground process.
- The router binds loopback only and supports bounded, text-only, non-streaming conversions between `/v1/messages` and `/v1/chat/completions`. It does not support tools, images, documents, structured outputs, retries, failover, or credential management.
- Router activity is bounded and redacted: it never records authorization values, endpoint URLs, request bodies, response bodies, or model names.

## MCP, Skills, and marketplace boundary

ModelToolbox manages local MCP and Skill metadata through explicit, revision-bound plans. Claude Code is the first write-enabled integration; Cursor, VS Code, Windsurf, Codex, and generic configurations remain inspection/export-only until each target contract has independent fixtures and verification.

The marketplace is disabled by default and its normal cache is local-only. When online catalog access is explicitly enabled in a future release, only curated trusted sources whose artifact integrity metadata validates may support one-click installation. Community and unknown sources remain browse/export-only. Third-party artifacts are user runtime data under the ModelToolbox home and never become project sources, dependencies, build inputs, or committed assets. Starting a local MCP process always requires explicit confirmation and the process is owned by the local bridge session.

## Layout

- `cli/` — the Python CLI process entry point and local bridge host.
- `flutter/` — Flutter desktop presentation client (Windows, macOS, Linux).
- `tui/` — npm-distributed terminal presentation client.
- `modules/` — dependency-layered first-party modules.
- `assets/` — original UI, data, and model assets.
- `tests/` — original unit, integration, and acceptance tests.
- `tools/` — first-party build, test, audit, and CI tooling.
- `docs/` — specifications, architecture, and governance records.

Read `docs/governance/originality-policy.md` before adding any content.
