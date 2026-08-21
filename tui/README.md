# ModelToolbox Terminal

`modeltoolbox` installs the dependency-free Node terminal client for ModelToolbox.

## Requirements

- Node.js 18 or newer
- A local ModelToolbox source checkout
- A Python executable capable of running that checkout
- An interactive terminal

The terminal client starts the local Python Bridge from the configured source checkout. It does not include or download Python, Flutter, models, credentials, or a remote service.

## Install

```sh
npm install -g modeltoolbox
```

## Start

Set the Python executable and the absolute path to the ModelToolbox checkout:

```powershell
$env:MODELTOOLBOX_PYTHON = "python"
$env:MODELTOOLBOX_ROOT = "C:\ModelToolbox"
mtb-tui
```

For a persistent Windows user configuration:

```powershell
[Environment]::SetEnvironmentVariable("MODELTOOLBOX_PYTHON", "python", "User")
[Environment]::SetEnvironmentVariable("MODELTOOLBOX_ROOT", "C:\ModelToolbox", "User")
```

Open a new terminal after setting persistent variables.

## Controls

- `1`–`7` or `Tab`: change workbench screen
- `r`: refresh local Bridge data
- `q` or `Ctrl+C`: exit

The Profiles and Router screens expose their available actions in the terminal footer. External configuration and local-process actions require explicit confirmation.

## Local commands

The source checkout provides the underlying local CLI and Bridge:

```text
python cli/main.py version
python cli/main.py integrations-list
python cli/main.py mcp-list
python cli/main.py marketplace-status
```

The TUI never records authorization headers, tokens, environment variable values, or routed request/response content.

## License

MIT. See [LICENSE](LICENSE).
