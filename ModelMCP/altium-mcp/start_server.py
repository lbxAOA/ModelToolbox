import subprocess
import sys
import traceback
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
VENV_DIR = SCRIPT_DIR / "server" / ".venv"
LOG_DIR = Path(r"C:/Users/Public/altium_mcp")
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LOG = LOG_DIR / "bootstrap.log"
except Exception:
    LOG = SCRIPT_DIR / "bootstrap.log"

def log(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(str(msg) + "\n")
    except Exception:
        pass

REQUIREMENTS = [
    "mcp[cli]==1.5.0",
    "pillow>=11.1.0",
    "pywin32>=310",
]

def ensure_venv():
    python_exe = VENV_DIR / "Scripts" / "python.exe"
    if python_exe.exists():
        return str(python_exe)
    log("creating venv with: " + sys.executable)
    subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])
    pip_exe = str(VENV_DIR / "Scripts" / "pip.exe")
    log("installing: " + ", ".join(REQUIREMENTS))
    subprocess.check_call([pip_exe, "install", "--quiet"] + REQUIREMENTS)
    log("venv ready")
    return str(python_exe)

if __name__ == "__main__":
    try:
        venv_python = ensure_venv()
        server_path = str(SCRIPT_DIR / "server" / "main.py")
        log("launching server: " + server_path)
        sys.exit(subprocess.call([venv_python, server_path]))
    except Exception:
        log("BOOTSTRAP FAILED:\n" + traceback.format_exc())
        raise
