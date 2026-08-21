"""ModelToolbox Next command-line application."""

from __future__ import annotations

import os
import sys
from io import TextIOBase
from pathlib import Path
from typing import Mapping, Sequence

from modules.command.model import Command, CommandContext, CommandResult, Option
from modules.command.parser import parse_command
from modules.command.registry import CommandRegistry
from modules.command.render import render_help, render_result
from modules.foundation.config import load_config
from modules.foundation.errors import CommandError, MtbError
from modules.foundation.logging import Logger
from modules.foundation.paths import resolve_app_paths
from modules.protocol.bridge import PROTOCOL, serve as serve_bridge
from modules.integrations.service import IntegrationService
from modules.marketplace.service import MarketplaceService
from modules.mcp.service import McpRuntimeService, McpService
from modules.profiles.service import ProfileService
from modules.router.policy import RouterPolicyService
from modules.skill.service import SkillService
from modules.router.server import serve as serve_router
from modules.ui.service import get_state_value, set_state_value

VERSION = "0.1.0"


def build_registry() -> CommandRegistry:
    registry = CommandRegistry()

    def version(_: CommandContext, __: Mapping[str, object]) -> CommandResult:
        return CommandResult(data={"name": "modeltoolbox-next", "version": VERSION}, message=VERSION)

    def config_show(context: CommandContext, _: Mapping[str, object]) -> CommandResult:
        data = {"home": str(context.paths.home), "output_format": context.config.output_format, "log_level": context.config.log_level}
        return CommandResult(data=data, message=f"home: {data['home']}\noutput_format: {data['output_format']}\nlog_level: {data['log_level']}")

    def state_get(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        key = str(values["key"])
        value = get_state_value(context.paths.state_dir, key)
        return CommandResult(data={"key": key, "value": value}, message=str(value))

    def state_set(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        import json
        key = str(values["key"])
        try:
            value = json.loads(str(values["value"]))
        except json.JSONDecodeError as error:
            raise CommandError("invalid-json-value", "State value must be valid JSON.") from error
        stored = set_state_value(context.paths.state_dir, key, value)
        return CommandResult(data={"key": key, "value": stored}, message=f"Stored: {key}")

    def profiles_adapters(context: CommandContext, _: Mapping[str, object]) -> CommandResult:
        data = ProfileService(context.paths.state_dir).list_adapters()
        rows = [f"{'enabled' if item['write_enabled'] else 'pending':<8} {item['id']:<16} {item['name']}" for item in data["adapters"]]
        return CommandResult(data=data, message="\n".join(rows))

    def profiles_list(context: CommandContext, _: Mapping[str, object]) -> CommandResult:
        data = ProfileService(context.paths.state_dir).list()
        rows = [f"{'*' if item['selected'] else ' '} {'enabled' if item['adapter_available'] else 'pending':<8} {item['id']:<18} {item['adapter_id']:<16} {item['base_url']}" for item in data["profiles"]]
        return CommandResult(data=data, message="\n".join(rows) if rows else "No profiles configured.")

    def profiles_show(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        data = ProfileService(context.paths.state_dir).get(values["profile_id"])
        return CommandResult(data=data, message=f"{data['name']} ({data['adapter_name']})\nAvailability: {'enabled' if data['adapter_available'] else 'pending'}\nURL: {data['base_url']}\nModel: {data['model'] or 'default'}")

    def profiles_create(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        payload = {
            "id": values["id"],
            "name": values["name"],
            "adapter_id": values["adapter_id"],
            "base_url": values["base_url"],
            "model": values.get("model"),
            "credential_source": values.get("credential_source"),
        }
        data = ProfileService(context.paths.state_dir).create(payload)
        return CommandResult(data=data, message=f"Created profile: {data['id']}")

    def profiles_update(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        payload = {
            "name": values["name"],
            "base_url": values["base_url"],
            "model": values.get("model"),
            "credential_source": values.get("credential_source"),
        }
        data = ProfileService(context.paths.state_dir).update(values["profile_id"], payload)
        return CommandResult(data=data, message=f"Updated profile: {data['id']}")

    def profiles_select(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        data = ProfileService(context.paths.state_dir).select(values["profile_id"])
        return CommandResult(data=data, message=f"Selected profile: {data['id']}")

    def profiles_inspect(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        data = ProfileService(context.paths.state_dir).inspect(values["profile_id"])
        message = data.get("message") or f"{data['target']}: {data['status']}"
        return CommandResult(data=data, message=message)

    def profiles_plan(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        data = ProfileService(context.paths.state_dir).plan_apply(values["profile_id"])
        changes = data["changes"]
        message = data.get("message") or ("No changes required." if not changes else "\n".join(f"{item['field']}: {item['from']!r} -> {item['to']!r}" for item in changes))
        return CommandResult(data=data, message=message)

    def profiles_apply(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        data = ProfileService(context.paths.state_dir).apply(values["profile_id"], values["revision"])
        return CommandResult(data=data, message=f"Applied profile to {data['target']}.")

    def profiles_delete(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        if not values.get("confirm"):
            raise CommandError("confirmation-required", "Delete requires --confirm.")
        ProfileService(context.paths.state_dir).delete(values["profile_id"])
        return CommandResult(data={"deleted": True}, message="Profile deleted.")

    def router_status(context: CommandContext, _: Mapping[str, object]) -> CommandResult:
        data = RouterPolicyService(context.paths.state_dir).status()
        return CommandResult(data=data, message=f"Router policy: {data['state']} (revision {data['revision']})")

    def router_plan(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        data = RouterPolicyService(context.paths.state_dir).plan_activate(values["profile_id"], values["inbound_protocol"], values["upstream_protocol"])
        changes = data["changes"]
        message = "No policy changes required." if not changes else "\n".join(f"{item['field']}: {item['from']!r} -> {item['to']!r}" for item in changes)
        return CommandResult(data=data, message=f"Current revision: {data['revision']}\nProposed revision: {data['next_revision']}\n{message}\nThis router supports bounded non-streaming text requests only.")

    def router_activate(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        if not values.get("confirm"):
            raise CommandError("confirmation-required", "Router activation requires --confirm.")
        data = RouterPolicyService(context.paths.state_dir).activate(values["profile_id"], values["inbound_protocol"], values["upstream_protocol"], int(str(values["expected_revision"])))
        return CommandResult(data=data, message=f"Activated router policy revision {data['revision']}.")

    def router_rollback(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        if not values.get("confirm"):
            raise CommandError("confirmation-required", "Router rollback requires --confirm.")
        data = RouterPolicyService(context.paths.state_dir).rollback(int(str(values["expected_revision"])))
        return CommandResult(data=data, message=f"Rolled back router policy to revision {data['revision']}.")

    def router_direct(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        if not values.get("confirm"):
            raise CommandError("confirmation-required", "Direct mode requires --confirm.")
        data = RouterPolicyService(context.paths.state_dir).direct(int(str(values["expected_revision"])))
        return CommandResult(data=data, message=f"Router is in direct mode at revision {data['revision']}.")

    def router_serve(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        serve_router(context.paths.state_dir, str(values.get("host") or "127.0.0.1"), int(values.get("port") or 15721))
        return CommandResult()

    def integrations_list(context: CommandContext, _: Mapping[str, object]) -> CommandResult:
        data = IntegrationService().list()
        return CommandResult(data=data, message="\n".join(f"{'enabled' if item['write_enabled'] else item['contract_status']:<12} {item['id']:<16} {item['name']}" for item in data["adapters"]))

    def mcp_list(context: CommandContext, _: Mapping[str, object]) -> CommandResult:
        data = McpService(context.paths.state_dir).list()
        return CommandResult(data=data, message="\n".join(f"{'enabled' if item['enabled'] else 'disabled':<8} {item['id']:<18} {item['transport']:<6} {item['name']}" for item in data["servers"]) or "No managed MCP servers.")

    def mcp_start(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        if not values.get("confirm"):
            raise CommandError("confirmation-required", "Starting an MCP process requires --confirm.")
        service = McpService(context.paths.state_dir)
        runtime = McpRuntimeService(service)
        try:
            data = runtime.start(values["mcp_id"])
            return CommandResult(data=data, message=f"MCP {data['id']} passed the process-start check. Persistent runtime control is available through the desktop or TUI bridge session.")
        finally:
            runtime.close()

    def marketplace_status(context: CommandContext, _: Mapping[str, object]) -> CommandResult:
        data = MarketplaceService(context.paths.state_dir).status()
        return CommandResult(data=data, message=data["message"])

    def marketplace_search(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        data = MarketplaceService(context.paths.state_dir).catalog(values.get("query") or "")
        return CommandResult(data=data, message="\n".join(f"{item['kind']:<5} {item['trust']:<9} {item['name']} {item['version']}" for item in data["items"]) or "No matching marketplace items.")

    def marketplace_recommendations(context: CommandContext, _: Mapping[str, object]) -> CommandResult:
        data = MarketplaceService(context.paths.state_dir).recommendations()
        return CommandResult(data=data, message="\n".join(f"{item['kind']:<5} {item['trust']:<9} {item['name']} {item['version']}" for item in data["items"]) or "No marketplace recommendations are cached.")

    def bridge(context: CommandContext, values: Mapping[str, object]) -> CommandResult:
        if values.get("protocol") != PROTOCOL:
            raise CommandError("unsupported-protocol", f"Bridge requires --protocol {PROTOCOL}.")
        serve_bridge(context.stdin, context.stdout, context.paths.state_dir, VERSION)
        return CommandResult()

    registry.register(Command("version", "Show the application version.", version))
    registry.register(Command("config", "Show active local configuration.", config_show))
    registry.register(Command("state-get", "Read a value from local state.", state_get, arguments=("key",)))
    registry.register(Command("state-set", "Write a JSON value to local state.", state_set, arguments=("key", "value")))
    registry.register(Command("profiles-adapters", "List supported and pending application adapters.", profiles_adapters))
    registry.register(Command("profiles-list", "List non-secret API configuration profiles.", profiles_list))
    registry.register(Command("profiles-show", "Show one non-secret profile.", profiles_show, arguments=("profile_id",)))
    registry.register(Command("profiles-create", "Create a non-secret profile.", profiles_create, options=(Option("id", takes_value=True, required=True, summary="Lower-case profile ID."), Option("name", takes_value=True, required=True, summary="Profile display name."), Option("adapter_id", takes_value=True, required=True, summary="claude-code, codex-cli, codex-desktop, or claude-desktop."), Option("base_url", takes_value=True, required=True, summary="HTTPS URL or loopback HTTP URL."), Option("model", takes_value=True, summary="Optional model identifier."), Option("credential_source", takes_value=True, summary="Optional environment-variable name; value is never read."))))
    registry.register(Command("profiles-update", "Update a non-secret profile without changing its ID or adapter.", profiles_update, arguments=("profile_id",), options=(Option("name", takes_value=True, required=True, summary="Profile display name."), Option("base_url", takes_value=True, required=True, summary="HTTPS URL or loopback HTTP URL."), Option("model", takes_value=True, summary="Optional model identifier; omit or pass empty to clear."), Option("credential_source", takes_value=True, summary="Optional environment-variable name; value is never read."))))
    registry.register(Command("profiles-select", "Select a profile without modifying external configuration.", profiles_select, arguments=("profile_id",)))
    registry.register(Command("profiles-inspect", "Inspect a target configuration without changing it.", profiles_inspect, arguments=("profile_id",)))
    registry.register(Command("profiles-plan", "Preview target configuration changes.", profiles_plan, arguments=("profile_id",)))
    registry.register(Command("profiles-apply", "Apply a previously previewed profile.", profiles_apply, arguments=("profile_id", "revision")))
    registry.register(Command("profiles-delete", "Delete a local profile.", profiles_delete, arguments=("profile_id",), options=(Option("confirm", summary="Confirm deletion."),)))
    registry.register(Command("router-status", "Show the active non-secret router policy.", router_status))
    registry.register(Command("router-plan", "Preview a router policy from a profile.", router_plan, arguments=("profile_id",), options=(Option("inbound_protocol", takes_value=True, required=True, summary="anthropic or openai."), Option("upstream_protocol", takes_value=True, required=True, summary="anthropic or openai."))))
    registry.register(Command("router-activate", "Activate a previewed router policy from a profile.", router_activate, arguments=("profile_id",), options=(Option("inbound_protocol", takes_value=True, required=True, summary="anthropic or openai."), Option("upstream_protocol", takes_value=True, required=True, summary="anthropic or openai."), Option("expected_revision", takes_value=True, required=True, summary="Current router policy revision."), Option("confirm", summary="Confirm policy activation."))))
    registry.register(Command("router-rollback", "Restore the previous router policy.", router_rollback, options=(Option("expected_revision", takes_value=True, required=True, summary="Current router policy revision."), Option("confirm", summary="Confirm policy rollback."))))
    registry.register(Command("router-direct", "Disable active router policy without deleting profiles.", router_direct, options=(Option("expected_revision", takes_value=True, required=True, summary="Current router policy revision."), Option("confirm", summary="Confirm direct mode."))))
    registry.register(Command("router-serve", "Run the loopback protocol router.", router_serve, options=(Option("host", takes_value=True, summary="Loopback host only."), Option("port", takes_value=True, summary="Loopback port."))))
    registry.register(Command("integrations-list", "List supported MCP and Skill application integrations.", integrations_list))
    registry.register(Command("mcp-list", "List locally managed MCP definitions.", mcp_list))
    registry.register(Command("mcp-start", "Start an enabled stdio MCP for this process session.", mcp_start, arguments=("mcp_id",), options=(Option("confirm", summary="Confirm local process start."),)))
    registry.register(Command("marketplace-status", "Show trusted marketplace cache and online status.", marketplace_status))
    registry.register(Command("marketplace-search", "Search the cached trusted marketplace catalog.", marketplace_search, options=(Option("query", takes_value=True, summary="Optional catalog search query."),)))
    registry.register(Command("marketplace-recommendations", "Show deterministic marketplace recommendations.", marketplace_recommendations))
    registry.register(Command("bridge", "Run the local presentation-client bridge.", bridge, options=(Option("protocol", takes_value=True, required=True, summary="Protocol version."),)))
    return registry


def main(
    argv: Sequence[str] | None = None,
    *,
    stdin: TextIOBase = sys.stdin,
    stdout: TextIOBase = sys.stdout,
    stderr: TextIOBase = sys.stderr,
    environ: Mapping[str, str] | None = None,
) -> int:
    tokens = list(sys.argv[1:] if argv is None else argv)
    environment = os.environ if environ is None else environ
    output_format = "json" if "--json" in tokens else "text"
    tokens = [token for token in tokens if token != "--json"]
    registry = build_registry()
    if not tokens or tokens == ["--help"]:
        stdout.write(render_help(registry))
        return 0
    command_name = tokens.pop(0)
    if command_name == "help":
        command = registry.get(tokens[0]) if tokens else None
        if tokens and command is None:
            stderr.write(f"Unknown command: {tokens[0]}\n")
            return 2
        stdout.write(render_help(registry, command))
        return 0
    command = registry.get(command_name)
    if command is None:
        stderr.write(f"Unknown command: {command_name}. Use 'mtb help'.\n")
        return 2
    if tokens == ["--help"]:
        stdout.write(render_help(registry, command))
        return 0
    try:
        paths = resolve_app_paths(Path(environment["MODELTOOLBOX_NEXT_HOME"]) if "MODELTOOLBOX_NEXT_HOME" in environment else None, environment)
        config = load_config(paths.config_file, environment, {"output_format": output_format})
        context = CommandContext(paths, config, stdin, stdout, stderr, Logger(stderr, config.log_level))
        parsed = parse_command(command, tokens)
        result = command.handler(context, parsed.values)
        render_result(result, output_format, stdout)
        return result.exit_code
    except CommandError as error:
        stderr.write(f"Error [{error.code}]: {error.message}\n")
        return 2
    except MtbError as error:
        stderr.write(f"Error [{error.code}]: {error.message}\n")
        return 3
    except Exception:
        stderr.write("Error [internal]: Unexpected internal failure.\n")
        return 70


if __name__ == "__main__":
    sys.exit(main())
