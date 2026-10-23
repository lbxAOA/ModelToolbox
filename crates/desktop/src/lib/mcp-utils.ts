import type { EnvVar } from "../components/env-editor";
import type { HttpHeader } from "../components/http-header-editor";
import type { TransportDto } from "../generated/dto";
import { keyPairToObject } from "./key-pair-utils";

// Static regex to avoid re-compilation on every call
const WHITESPACE_REGEX = /\s+/;

export type McpImportTransportType = "stdio" | "sse" | "streamable_http";

export interface McpImportServerConfig {
	type?: McpImportTransportType;
	command?: string;
	args?: string[];
	env?: Record<string, string>;
	url?: string;
	headers?: Record<string, string>;
	timeout?: number;
}

export interface McpImportJson {
	mcpServers?: Record<string, McpImportServerConfig>;
}

export function buildTransportFromForm(
	transportType: "stdio" | "sse" | "streamable_http",
	data: {
		command?: string;
		args?: string;
		envVars?: EnvVar[];
		url?: string;
		httpHeaders?: HttpHeader[];
		timeout?: string;
	},
): TransportDto | undefined {
	const timeoutNum = data.timeout ? Number.parseInt(data.timeout, 10) : null;

	if (transportType === "stdio") {
		const argsArray = data.args?.trim()
			? data.args.trim().split(WHITESPACE_REGEX)
			: [];
		const envRecord: Record<string, string> | null =
			data.envVars && data.envVars.length > 0
				? keyPairToObject(data.envVars)
				: null;

		return {
			type: "stdio",
			command: data.command?.trim() ?? "",
			args: argsArray,
			env: envRecord,
			timeout: timeoutNum,
		};
	}

	const headersRecord: Record<string, string> | null =
		data.httpHeaders && data.httpHeaders.length > 0
			? keyPairToObject(data.httpHeaders)
			: null;

	return {
		type: transportType,
		url: data.url?.trim() ?? "",
		headers: headersRecord,
		timeout: timeoutNum,
	};
}

export function capitalize(str: string): string {
	return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

export function getImportedMcpTransportType(
	config: McpImportServerConfig,
): McpImportTransportType | null {
	if (config.command) {
		return "stdio";
	}

	if (config.url) {
		return config.type === "streamable_http" ? "streamable_http" : "sse";
	}

	return null;
}

export function toMcpImportServerConfig(
	transport: TransportDto,
): McpImportServerConfig {
	if (transport.type === "stdio") {
		return {
			command: transport.command,
			...(transport.args.length > 0 ? { args: transport.args } : {}),
			...(transport.env ? { env: transport.env } : {}),
			...(transport.timeout !== null
				? { timeout: transport.timeout }
				: {}),
		};
	}

	return {
		url: transport.url,
		...(transport.type === "streamable_http"
			? { type: transport.type }
			: {}),
		...(transport.headers ? { headers: transport.headers } : {}),
		...(transport.timeout !== null ? { timeout: transport.timeout } : {}),
	};
}

export function serializeMcpImportJson(
	name: string,
	transport: TransportDto,
): string {
	return JSON.stringify(
		{
			mcpServers: {
				[name]: toMcpImportServerConfig(transport),
			},
		},
		null,
		2,
	);
}
