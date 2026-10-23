# model-toolbox - Code Agent Management Tool
# https://github.com/akarachen/model-toolbox

set windows-shell := ["cmd.exe", "/c"]

# The ccusage sidecar is only needed for a real `tauri build` bundle. Workspace
# recipes (test/lint) build the desktop crate's build.rs too, which would
# otherwise fetch the sidecar from npm; skip it so the dev loop stays offline and
# needs no network. A real bundle runs `tauri build` directly, outside just.
export MODEL_TOOLBOX_SKIP_SIDECAR := "1"

# model-toolbox-v2 is a macOS-only GPUI app (its deps and code are gated on macOS), so
# workspace-wide checks skip it on other hosts to stay green on Linux/Windows.
model_toolbox_v2_exclude := if os() == "macos" { "" } else { "--exclude model-toolbox-v2" }

# Default recipe - build the CLI
default: build

# Build the CLI binary (model-toolbox-cli)
build:
    cargo build --release -p model-toolbox-cli

# Build for development
dev:
    cargo build -p model-toolbox-cli

# Run all tests
test:
    cargo test --workspace {{model_toolbox_v2_exclude}}

# Run integration tests only
integration-test:
    cargo test -p model-toolbox-core --test integration_tests

# Run tests with agent validation (requires claude/opencode CLIs)
test-with-validation:
    cargo test --workspace --features agent-validation

# Format code
fmt:
	cargo fmt --all
	bun run format

# Run clippy linter
lint:
    cargo clippy --workspace {{model_toolbox_v2_exclude}} -- -D warnings
    cd ./crates/desktop && nr lint

# Clean build artifacts
clean:
    cargo clean

# Install model-toolbox-cli to ~/.cargo/bin
install: build
    cp target/release/model-toolbox-cli ~/.cargo/bin/

# Run model-toolbox-cli with --help
help: dev
    ./target/debug/model-toolbox-cli --help

# Run with cargo (pass args: just start -- --arg)
start *args:
    cargo run -p model-toolbox-cli -- {{args}}

desktop:
    cd ./crates/desktop && nr start

# Bump version across all manifests
bump version:
    sed -i '' 's/^version = .*/version = "{{version}}"/' Cargo.toml
    sed -i '' 's/"version": ".*"/"version": "{{version}}"/' crates/desktop/package.json
    sed -i '' 's/"version": ".*"/"version": "{{version}}"/' crates/desktop/src-tauri/tauri.conf.json || true
