#!/usr/bin/env node
const { existsSync, readdirSync } = require("node:fs");
const { join } = require("node:path");
const { spawnSync } = require("node:child_process");

if (process.env.MODELTOOLBOX_SKIP_INSTALL === "1") {
  console.log("Skipping installation (MODELTOOLBOX_SKIP_INSTALL=1)");
  process.exit(0);
}

const root = join(__dirname, "..");
const isWindows = process.platform === "win32";
const venvPython = join(root, ".venv", isWindows ? "Scripts" : "bin", isWindows ? "python.exe" : "python");
const wheelsDir = join(root, "wheels");

function run(command, args, cwd = root) {
  const result = spawnSync(command, args, { cwd, stdio: "inherit", shell: false });
  if (result.error) {
    console.error(`Failed to execute: ${command} ${args.join(" ")}`);
    throw result.error;
  }
  if (result.status !== 0) {
    process.exit(result.status || 1);
  }
}

function getPythonVersion(pythonCmd, args = []) {
  const result = spawnSync(pythonCmd, [...args, "--version"], { stdio: "pipe", shell: false });
  if (result.status === 0 && result.stdout) {
    const output = result.stdout.toString().trim();
    const match = output.match(/Python (\d+)\.(\d+)/);
    if (match) {
      return { major: parseInt(match[1]), minor: parseInt(match[2]) };
    }
  }
  return null;
}

function findPython() {
  if (process.env.MODELTOOLBOX_PYTHON) {
    const version = getPythonVersion(process.env.MODELTOOLBOX_PYTHON);
    if (version && version.major === 3 && version.minor >= 11) {
      return { command: process.env.MODELTOOLBOX_PYTHON, argsPrefix: [] };
    }
    console.warn(`Warning: MODELTOOLBOX_PYTHON points to Python ${version?.major}.${version?.minor}, but Python 3.11+ is required.`);
  }

  const candidates = isWindows
    ? [
        { command: "py", argsPrefix: ["-3.12"] },
        { command: "py", argsPrefix: ["-3.11"] },
        { command: "python", argsPrefix: [] },
      ]
    : [
        { command: "python3.12", argsPrefix: [] },
        { command: "python3.11", argsPrefix: [] },
        { command: "python3", argsPrefix: [] },
        { command: "python", argsPrefix: [] },
      ];

  for (const candidate of candidates) {
    const version = getPythonVersion(candidate.command, candidate.argsPrefix);
    if (version && version.major === 3 && version.minor >= 11) {
      return candidate;
    }
  }

  console.error("Error: Python 3.11 or newer is required but not found.");
  console.error("Please install Python 3.11+ from https://www.python.org/downloads/");
  console.error("Or set MODELTOOLBOX_PYTHON environment variable to your Python executable.");
  process.exit(1);
}

if (!existsSync(venvPython)) {
  console.log("Setting up ModelToolbox Python environment...");
  
  const python = findPython();
  const version = getPythonVersion(python.command, python.argsPrefix);
  console.log(`Using Python ${version.major}.${version.minor}`);

  console.log("Creating virtual environment...");
  run(python.command, [...python.argsPrefix, "-m", "venv", ".venv"]);

  const useWheels = existsSync(wheelsDir);
  
  if (useWheels) {
    console.log("Installing from pre-built wheels...");
    const wheels = readdirSync(wheelsDir).filter(f => f.endsWith(".whl"));
    
    if (wheels.length === 0) {
      console.warn("Warning: wheels/ directory exists but contains no .whl files. Falling back to source installation.");
    } else {
      run(venvPython, ["-m", "pip", "install", "--no-cache-dir", "--upgrade", "pip"]);
      
      for (const wheel of wheels) {
        run(venvPython, ["-m", "pip", "install", "--no-cache-dir", join(wheelsDir, wheel)]);
      }
      
      run(venvPython, ["-m", "pip", "install", "--no-cache-dir", "textual>=0.88.0"]);
      console.log("✓ Installation complete!");
      process.exit(0);
    }
  }

  console.log("Installing from source (development mode)...");
  run(venvPython, ["-m", "pip", "install", "--no-cache-dir", "--upgrade", "pip"]);
  run(venvPython, ["-m", "pip", "install", "--no-cache-dir", join(root, "ModelCore")]);
  run(venvPython, ["-m", "pip", "install", "--no-cache-dir", join(root, "ModelProvider")]);
  run(venvPython, ["-m", "pip", "install", "--no-cache-dir", join(root, "ModelSkill")]);
  run(venvPython, ["-m", "pip", "install", "--no-cache-dir", join(root, "ModelMCP")]);
  run(venvPython, ["-m", "pip", "install", "--no-cache-dir", "textual>=0.88.0"]);
  console.log("✓ Installation complete!");
} else {
  console.log("Virtual environment already exists. Skipping installation.");
  console.log("To reinstall, delete .venv directory or run: npm rebuild modeltoolbox");
}
