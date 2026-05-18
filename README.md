# tuskr-cli

Command-line interface for the [Tuskr](https://tuskr.app) test management API.

## Install

```bash
pipx install tuskr-cli
# or
pip install tuskr-cli
```

## Claude Code Plugin

Install the tuskr skill directly into Claude Code via the plugin marketplace:

```bash
/plugin marketplace add harish-talview/tuskr-cli
/plugin install tuskr-skill@tuskr
```

Once installed, Claude Code will use the tuskr skill automatically when you ask about Tuskr test management. You can also invoke it directly:

```bash
/tuskr-skill:tuskr
```

## Quick Start

Get your API token from Tuskr → Top Menu → User Profile Icon → API.

```bash
tuskr config set --token YOUR_TOKEN --tenant-id YOUR_TENANT_ID
tuskr config validate
```

## Commands

| Group | Command | Description |
|-------|---------|-------------|
| `config` | `set` | Save credentials |
| `config` | `show` | Print current credentials (token masked) |
| `config` | `validate` | Verify credentials against the API |
| `project` | `list` | List projects |
| `project` | `create` | Create a project |
| `case` | `list` | List test cases |
| `case` | `create` | Create a test case |
| `case` | `upsert` | Upsert a test case from JSON |
| `case` | `import` | Bulk import test cases from JSON |
| `run` | `list` | List test runs |
| `run` | `create` | Create a test run |
| `run` | `results` | Get results for a test run |
| `run` | `add-results` | Bulk-add results from JSON |
| `run` | `import-junit` | Import results from JUnit XML |
| `suite` | `list` | List test suites |

All list commands support `--limit`, `--offset`, and `--json` (machine-readable output).

## Examples

```bash
# List all projects
tuskr project list

# List test cases in a project
tuskr case list --project-id <PROJECT_ID>

# Create a test run
tuskr run create --name "Sprint 12 regression" --project-id <PROJECT_ID>

# Import JUnit XML results from CI
tuskr run import-junit --run-id <RUN_ID> --project-id <PROJECT_ID> --file results.xml

# Check what failed
tuskr run results <RUN_ID> --status failed --json
```

## API Reference

https://tuskr.app/kb/latest/api

## License

MIT
