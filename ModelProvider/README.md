# ModelProvider

Provider management for ModelToolbox: runtime and provider switching.

## Features

- **Provider Registry**: Manage multiple LLM providers
- **Runtime Switching**: Switch between providers at runtime
- **Environment Management**: Provider-specific environment configuration
- **Provider Types**: Support for OpenAI, Anthropic, Ollama, and custom providers

## Installation

```bash
pip install modeltoolbox-provider
```

For development:

```bash
pip install -e "ModelProvider[dev]"
```

## Usage

### List Providers

```bash
mtb provider list
```

### Switch Provider

```bash
mtb provider switch openai
```

### Configure Provider

```bash
mtb provider config anthropic --api-key sk-...
```

## Development

Run tests:

```bash
pytest ModelProvider/tests/
```

## License

MIT
