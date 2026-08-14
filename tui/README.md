# ModelToolbox Terminal Workbench

A dependency-free native terminal shell for the ModelToolbox local bridge.

## Requirements

- Node.js 18 or later.
- A configured ModelToolbox checkout and Python executable.
- `MODELTOOLBOX_ROOT` pointing to the checkout root.
- `MODELTOOLBOX_PYTHON` pointing to the Python executable that runs the CLI bridge.

## Run

```powershell
$env:MODELTOOLBOX_ROOT = "C:\ModelToolbox"
$env:MODELTOOLBOX_PYTHON = "C:\Path\To\python.exe"
node .\bin\mtb-tui.mjs
```

The client starts the local `mtb bridge --protocol mtb.bridge/1` process and never reads Foundation state or workspace files directly.

## Controls

- `1`–`5`: select Overview, Session, Workspace, Tools, or Settings.
- `Tab`: select the next screen.
- `r`: refresh the bridge snapshot.
- `q` or `Ctrl+C`: restore the terminal and exit.

Session streaming, tool execution, workspace browsing, and settings edits are intentionally represented as safe framework placeholders until their independent ModelToolbox domain specifications are implemented.

## Test

```powershell
node --test .\test\*.test.mjs
```
