#!/usr/bin/env node
const { existsSync } = require("node:fs");
const { join } = require("node:path");
const { spawnSync } = require("node:child_process");

const root = join(__dirname, "..");
const isWindows = process.platform === "win32";
const venvPython = join(root, ".venv", isWindows ? "Scripts" : "bin", isWindows ? "python.exe" : "python");

function run(command, args) {
  const result = spawnSync(command, args, { cwd: root, stdio: "inherit", shell: false });
  if (result.error) {
    throw result.error;
  }
  if (result.status !== 0) {
    process.exit(result.status || 1);
  }
}

function findPython() {
  if (process.env.MODELTOOLBOX_PYTHON) {
    return { command: process.env.MODELTOOLBOX_PYTHON, argsPrefix: [] };
  }
  if (isWindows) {
    const probe = spawnSync("py", ["-3.11", "--version"], { stdio: "ignore", shell: false });
    if (probe.status === 0) {
      return { command: "py", argsPrefix: ["-3.11"] };
    }
  }
  return { command: "python", argsPrefix: [] };
}

if (!existsSync(venvPython)) {
  const python = findPython();
  run(python.command, [...python.argsPrefix, "-m", "venv", ".venv"]);
}

run(venvPython, ["-m", "pip", "install", "-e", "."]);
