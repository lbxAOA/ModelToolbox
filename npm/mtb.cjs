#!/usr/bin/env node
const { existsSync } = require("node:fs");
const { join } = require("node:path");
const { spawnSync } = require("node:child_process");

const root = join(__dirname, "..");
const isWindows = process.platform === "win32";
const venvPython = join(root, ".venv", isWindows ? "Scripts" : "bin", isWindows ? "python.exe" : "python");
const mtbCore = join(root, ".venv", isWindows ? "Scripts" : "bin", isWindows ? "mtb-core.exe" : "mtb-core");

if (!existsSync(venvPython)) {
  console.error("Error: ModelToolbox Python environment not found.");
  console.error("");
  console.error("The virtual environment is missing or corrupted.");
  console.error("To fix this, run:");
  console.error("  npm rebuild modeltoolbox");
  console.error("");
  console.error("If the problem persists:");
  console.error("  1. Ensure Python 3.11+ is installed");
  console.error("  2. Check npm install scripts are enabled");
  console.error("  3. Run 'npm install -g modeltoolbox' again");
  process.exit(1);
}

if (!existsSync(mtbCore)) {
  console.error("Error: mtb-core command not found in virtual environment.");
  console.error("");
  console.error("The Python packages may not be installed correctly.");
  console.error("To fix this, run:");
  console.error("  npm rebuild modeltoolbox");
  console.error("");
  console.error("Virtual environment location:");
  console.error(`  ${root}`);
  console.error("");
  console.error("For troubleshooting, run:");
  console.error(`  ${venvPython} -m pip list`);
  process.exit(1);
}

const args = process.argv.slice(2);
const result = spawnSync(mtbCore, args, { 
  cwd: process.cwd(), 
  stdio: "inherit", 
  shell: false 
});

if (result.error) {
  console.error("Error: Failed to execute mtb-core");
  console.error(result.error.message);
  console.error("");
  console.error("This may indicate a problem with the Python environment.");
  console.error("Try rebuilding: npm rebuild modeltoolbox");
  process.exit(1);
}

process.exit(result.status || 0);
