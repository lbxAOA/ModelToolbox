# ModelSkill

Skill management for ModelToolbox: skill registry and library management.

## Features

- **Skill Registry**: Manage and discover skills
- **Library Management**: Install and organize skill libraries
- **Skill Discovery**: Search and browse available skills
- **Version Control**: Track skill versions and updates

## Installation

```bash
pip install modeltoolbox-skill
```

For development:

```bash
pip install -e "ModelSkill[dev]"
```

## Usage

### List Skills

```bash
mtb skill list
```

### Install Skill

```bash
mtb skill install <skill-name>
```

### Search Skills

```bash
mtb skill search <query>
```

## Development

Run tests:

```bash
pytest ModelSkill/tests/
```

## License

MIT
