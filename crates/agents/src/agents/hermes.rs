use crate::descriptor::*;
use crate::models::{AgentConfig, McpServer, McpTransport};
use serde_yaml::{Mapping, Value};
use std::collections::HashMap;
use std::path::{Path, PathBuf};

fn hermes_home() -> Option<PathBuf> {
	std::env::var_os("HERMES_HOME")
		.map(PathBuf::from)
		.or_else(|| {
			if cfg!(windows) {
				std::env::var_os("LOCALAPPDATA")
					.map(|dir| PathBuf::from(dir).join("hermes"))
			} else {
				home_dir().map(|home| home.join(".hermes"))
			}
		})
}

fn mcp_global_path() -> Option<PathBuf> {
	hermes_home().map(|home| home.join("config.yaml"))
}

fn global_data_dir() -> Option<PathBuf> {
	hermes_home()
}

fn global_skills_paths() -> Vec<PathBuf> {
	hermes_home()
		.map(|home| vec![home.join("skills")])
		.unwrap_or_default()
}

fn project_skills_paths(root: &Path) -> Vec<PathBuf> {
	vec![root.join(".hermes/skills"), root.join(".agents/skills")]
}

fn global_skill_write_path() -> Option<PathBuf> {
	hermes_home().map(|home| home.join("skills"))
}

fn project_skill_write_path(root: &Path) -> Option<PathBuf> {
	Some(root.join(".hermes/skills"))
}

fn global_rule_paths() -> Vec<PathBuf> {
	hermes_home()
		.map(|home| vec![home.join("SOUL.md")])
		.unwrap_or_default()
}

fn project_rule_paths(root: &Path) -> Vec<PathBuf> {
	vec![root.join("AGENTS.md")]
}

fn string_value(mapping: &Mapping, key: &str) -> Option<String> {
	mapping
		.get(Value::String(key.to_string()))
		.and_then(Value::as_str)
		.map(ToOwned::to_owned)
}

fn bool_value(mapping: &Mapping, key: &str) -> Option<bool> {
	mapping
		.get(Value::String(key.to_string()))
		.and_then(Value::as_bool)
}

fn u64_value(mapping: &Mapping, key: &str) -> Option<u64> {
	mapping
		.get(Value::String(key.to_string()))
		.and_then(Value::as_u64)
}

fn string_list(mapping: &Mapping, key: &str) -> Vec<String> {
	mapping
		.get(Value::String(key.to_string()))
		.and_then(Value::as_sequence)
		.map(|items| {
			items
				.iter()
				.filter_map(Value::as_str)
				.map(ToOwned::to_owned)
				.collect()
		})
		.unwrap_or_default()
}

fn string_map(mapping: &Mapping, key: &str) -> Option<HashMap<String, String>> {
	let map = mapping
		.get(Value::String(key.to_string()))
		.and_then(Value::as_mapping)?;
	let values = map
		.iter()
		.filter_map(|(key, value)| {
			Some((key.as_str()?.to_string(), value.as_str()?.to_string()))
		})
		.collect::<HashMap<_, _>>();
	Some(values)
}

fn parse_entry(name: &str, value: &Value) -> Option<McpServer> {
	let mapping = value.as_mapping()?;
	let transport = if let Some(command) = string_value(mapping, "command") {
		McpTransport::Stdio {
			command,
			args: string_list(mapping, "args"),
			env: string_map(mapping, "env"),
			timeout: u64_value(mapping, "timeout"),
		}
	} else {
		let url = string_value(mapping, "url")?;
		if string_value(mapping, "transport").as_deref() == Some("sse") {
			McpTransport::Sse {
				url,
				headers: string_map(mapping, "headers"),
				timeout: u64_value(mapping, "timeout"),
			}
		} else {
			McpTransport::StreamableHttp {
				url,
				headers: string_map(mapping, "headers"),
				timeout: u64_value(mapping, "timeout"),
			}
		}
	};
	let mut server = McpServer::new(name, transport);
	server.enabled = bool_value(mapping, "enabled").unwrap_or(true);
	server.timeout = u64_value(mapping, "timeout");
	server.source_name = Some(name.to_string());
	Some(server)
}

pub fn parse(content: &str) -> crate::Result<AgentConfig> {
	let Some(root) =
		serde_yaml::from_str::<Option<Value>>(content).map_err(|error| {
			crate::ConfigError::InvalidConfig(error.to_string())
		})?
	else {
		return Ok(AgentConfig::new());
	};
	let mut config = AgentConfig::new();
	let Some(servers) = root.get("mcp_servers").and_then(Value::as_mapping)
	else {
		return Ok(config);
	};
	for (name, value) in servers {
		if let Some(name) = name.as_str() {
			if let Some(server) = parse_entry(name, value) {
				config.mcps.push(server);
			}
		}
	}
	Ok(config)
}

fn scalar_map(entries: &HashMap<String, String>) -> Value {
	let mut map = Mapping::new();
	for (key, value) in entries {
		map.insert(Value::String(key.clone()), Value::String(value.clone()));
	}
	Value::Mapping(map)
}

fn update_entry(entry: &mut Mapping, server: &McpServer) {
	for key in [
		"command",
		"args",
		"env",
		"url",
		"headers",
		"transport",
		"enabled",
		"timeout",
	] {
		entry.remove(Value::String(key.to_string()));
	}
	match &server.transport {
		McpTransport::Stdio {
			command,
			args,
			env,
			timeout,
		} => {
			entry.insert(
				Value::String("command".to_string()),
				Value::String(command.clone()),
			);
			if !args.is_empty() {
				entry.insert(
					Value::String("args".to_string()),
					Value::Sequence(
						args.iter().cloned().map(Value::String).collect(),
					),
				);
			}
			if let Some(env) = env {
				entry.insert(Value::String("env".to_string()), scalar_map(env));
			}
			if let Some(timeout) = timeout {
				entry.insert(
					Value::String("timeout".to_string()),
					Value::Number((*timeout).into()),
				);
			}
		}
		McpTransport::Sse {
			url,
			headers,
			timeout,
		}
		| McpTransport::StreamableHttp {
			url,
			headers,
			timeout,
		} => {
			entry.insert(
				Value::String("url".to_string()),
				Value::String(url.clone()),
			);
			if matches!(server.transport, McpTransport::Sse { .. }) {
				entry.insert(
					Value::String("transport".to_string()),
					Value::String("sse".to_string()),
				);
			}
			if let Some(headers) = headers {
				entry.insert(
					Value::String("headers".to_string()),
					scalar_map(headers),
				);
			}
			if let Some(timeout) = timeout {
				entry.insert(
					Value::String("timeout".to_string()),
					Value::Number((*timeout).into()),
				);
			}
		}
	}
	if !server.enabled {
		entry.insert(Value::String("enabled".to_string()), Value::Bool(false));
	}
}

pub fn serialize(
	config: &AgentConfig,
	original: Option<&str>,
) -> crate::Result<String> {
	let mut root =
		serde_yaml::from_str::<Option<Value>>(original.unwrap_or(""))
			.map_err(|error| {
				crate::ConfigError::InvalidConfig(error.to_string())
			})?
			.unwrap_or_else(|| Value::Mapping(Mapping::new()));
	let root_map = root.as_mapping_mut().ok_or_else(|| {
		crate::ConfigError::InvalidConfig(
			"Hermes config root must be a mapping".to_string(),
		)
	})?;
	let servers = root_map
		.entry(Value::String("mcp_servers".to_string()))
		.or_insert_with(|| Value::Mapping(Mapping::new()))
		.as_mapping_mut()
		.ok_or_else(|| {
			crate::ConfigError::InvalidConfig(
				"mcp_servers must be a mapping".to_string(),
			)
		})?;
	let existing_names = servers
		.iter()
		.filter_map(|(name, value)| {
			let name = name.as_str()?;
			parse_entry(name, value).map(|_| name.to_string())
		})
		.collect::<Vec<_>>();
	let known_names = config
		.mcps
		.iter()
		.map(|server| server.name.as_str())
		.collect::<std::collections::HashSet<_>>();
	for name in existing_names {
		if !known_names.contains(name.as_str()) {
			servers.remove(Value::String(name));
		}
	}
	for server in &config.mcps {
		let source_name = server.source_name.as_deref().unwrap_or(&server.name);
		if source_name != server.name {
			return Err(crate::ConfigError::resource_exists(
				"MCP server",
				&server.name,
			));
		}
		let entry = servers
			.entry(Value::String(server.name.clone()))
			.or_insert_with(|| Value::Mapping(Mapping::new()));
		update_entry(
			entry.as_mapping_mut().ok_or_else(|| {
				crate::ConfigError::InvalidConfig(format!(
					"MCP '{}' must be a mapping",
					server.name
				))
			})?,
			server,
		);
	}
	serde_yaml::to_string(&root)
		.map_err(|error| crate::ConfigError::InvalidConfig(error.to_string()))
}

fn load_mcps(
	project_root: Option<&Path>,
	scope: crate::ResourceScope,
) -> crate::Result<Vec<McpServer>> {
	load_scoped_mcps(project_root, scope, Some(mcp_global_path), None, parse)
}

fn save_mcps(
	project_root: Option<&Path>,
	scope: crate::ResourceScope,
	mcps: &[McpServer],
) -> crate::Result<()> {
	save_scoped_mcps(
		project_root,
		scope,
		mcps,
		Some(mcp_global_path),
		None,
		serialize,
	)
}

pub const DESCRIPTOR: AgentDescriptor = AgentDescriptor {
	id: "hermes",
	display_name: "Hermes Agent",
	mcp_parse_config: Some(parse),
	mcp_serialize_config: Some(serialize),
	load_mcps,
	save_mcps,
	mcp_global_path: Some(mcp_global_path),
	mcp_project_path: None,
	global_data_dir,
	capabilities: Capabilities {
		skills: SkillCapabilities {
			scopes: ScopeSupport {
				global: true,
				project: true,
			},
			universal: true,
		},
		mcp: McpCapabilities {
			scopes: ScopeSupport {
				global: true,
				project: false,
			},
			stdio: true,
			sse: true,
			streamable_http: true,
			enable_disable: true,
		},
		sub_agents: SubAgentCapabilities {
			scopes: ScopeSupport {
				global: false,
				project: false,
			},
		},
	},
	global_skill_paths: Some(GlobalSkillPaths {
		read: global_skills_paths,
		write: global_skill_write_path,
	}),
	project_skill_paths: Some(ProjectSkillPaths {
		read: project_skills_paths,
		write: project_skill_write_path,
	}),
	load_sub_agents: load_sub_agents_noop,
	save_sub_agents: save_sub_agents_noop,
	cli_name: "hermes",
	validate_args: &["--version"],
	project_markers: &[".hermes"],
	skills_cli_name: None,
	rule_paths: Some(RulePaths {
		global: Some(global_rule_paths),
		project: Some(project_rule_paths),
	}),
};
