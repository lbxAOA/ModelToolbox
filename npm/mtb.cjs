#!/usr/bin/env node
const { existsSync } = require("node:fs");
const { join } = require("node:path");
const { spawnSync } = require("node:child_process");

const root = join(__dirname, "..");
const isWindows = process.platform === "win32";
const venvPython = join(root, ".venv", isWindows ? "Scripts" : "bin", isWindows ? "python.exe" : "python");
const mtbCore = join(root, ".venv", isWindows ? "Scripts" : "bin", isWindows ? "mtb-core.exe" : "mtb-core");

if (!existsSync(venvPython)) {
  console.error("Error: Python virtual environment not found.");
  console.error("Run: npm run bootstrap");
  process.exit(1);
}

if (!existsSync(mtbCore)) {
  console.error("Error: mtb-core not found in virtual environment.");
  console.error("Run: npm run bootstrap");
  process.exit(1);
}

const args = process.argv.slice(2);
const result = spawnSync(mtbCore, args, { 
  cwd: process.cwd(), 
  stdio: "inherit", 
  shell: false 
});

process.exit(result.status || 0);
