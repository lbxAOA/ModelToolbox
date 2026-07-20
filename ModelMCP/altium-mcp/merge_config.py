"""Merge altium-mcp into Claude Desktop's claude_desktop_config.json (with backup)."""
import json, os, shutil, sys, time

APPDATA = os.environ.get("APPDATA", "")
CFG_DIR = os.path.join(APPDATA, "Claude")
CFG = os.path.join(CFG_DIR, "claude_desktop_config.json")

PYTHON = r"C:\Users\rdft1\AppData\Local\Programs\Python\Python312\python.exe"
ENTRY = {
    "command": PYTHON,
    "args": [r"C:\MyApp\altium-mcp\start_server.py"],
}

def main():
    if not os.path.isdir(CFG_DIR):
        print("ERROR: Claude config dir not found:", CFG_DIR)
        print("Is Claude Desktop installed for this user?")
        return 1
    if not os.path.isfile(PYTHON):
        print("ERROR: python.exe not found:", PYTHON)
        return 1

    data = {}
    if os.path.isfile(CFG):
        backup = CFG + ".bak." + time.strftime("%Y%m%d%H%M%S")
        shutil.copy2(CFG, backup)
        print("Backup created:", backup)
        try:
            with open(CFG, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print("WARNING: existing config unreadable (%s); starting fresh." % e)
            data = {}

    data.setdefault("mcpServers", {})["altium-mcp"] = ENTRY

    with open(CFG, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("OK: altium-mcp added to", CFG)
    print(json.dumps(data["mcpServers"]["altium-mcp"], indent=2))
    print()
    print("NEXT: fully quit Claude Desktop (tray icon > Quit), reopen it,")
    print("then open Altium Designer with your project.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
