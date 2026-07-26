#!/usr/bin/env node
const { existsSync } = require("node:fs");
const { join } = require("node:path");
const { spawnSync } = require("node:child_process");

const root = join(__dirname, "..");
const isWindows = process.platform === "win32";
const binDir = join(root, ".venv", isWindows ? "Scripts" : "bin");
const mtb = join(binDir, isWindows ? "mtb.exe" : "mtb");
const bootstrap = join(__dirname, "bootstrap.cjs");

function run(command, args) {
  const result = spawnSync(command, args, { cwd: root, stdio: "inherit", shell: false });
  if (result.error) {
    console.error(result.error.message);
    process.exit(1);
  }
  process.exit(result.status === null ? 1 : result.status);
}

if (!existsSync(mtb)) {
  const boot = spawnSync(process.execPath, [bootstrap], { cwd: root, stdio: "inherit", shell: false });
  if (boot.error) {
    console.error(boot.error.message);
    process.exit(1);
  }
  if (boot.status !== 0) {
    process.exit(boot.status || 1);
  }
}

run(mtb, process.argv.slice(2));
