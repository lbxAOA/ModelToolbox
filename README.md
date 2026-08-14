# ModelToolbox Next

ModelToolbox Next is an isolated, clean-room implementation workspace for the next self-developed ModelToolbox release.

## Delivery boundary

Only content under this directory is eligible for future delivery. It must contain no third-party source code, libraries, static assets, model weights, datasets, build tools, or test frameworks. Python 3.11+ and its standard library are supported platform prerequisites. Flutter/Dart SDK and its SDK-owned `flutter` and `flutter_test` libraries are additionally approved platform prerequisites for the `flutter/` desktop presentation client; no non-SDK pub package is allowed. Node.js and npm are approved only for the dependency-free `tui/` terminal package and its artifact transport; neither may install, download, or resolve dependencies. The operating system and hardware drivers remain external platform prerequisites.

GitHub remains source and release hosting, npm remains the distribution channel for the terminal client, and GitHub Releases host native Flutter installers. Neither GitHub Actions nor third-party build, test, packaging, or runtime dependencies belong to this workspace.

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
