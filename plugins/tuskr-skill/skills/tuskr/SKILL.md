---
name: tuskr
description: Interact with the Tuskr test management API — list projects, manage test cases, create and query test runs, import JUnit XML results
---

Use the `tuskr` CLI to manage projects, test cases, test runs, and results in Tuskr.

## Setup check

Before any Tuskr operation, verify the CLI is available:

```bash
tuskr config show
```

If the command is not found, install it:
```bash
pipx install tuskr-cli
```

If config is missing, ask the user for their token and tenant ID, then run:
```bash
tuskr config set --token <TOKEN> --tenant-id <TENANT_ID>
```
Token location: Tuskr → Top Menu → User Profile Icon → API.

## How to fulfill common requests

**"List my projects"**
```bash
tuskr project list --json
```

**"List test cases [in project X]"**
```bash
tuskr case list --project-id <ID> --json
```

**"Create a test run"**
```bash
tuskr run create --name "<name>" --project-id <ID> --json
```
Capture `data.id` from the output for follow-up commands.

**"Check what failed in a run"**
```bash
tuskr run results <RUN_ID> --status failed --json
```

**"Import JUnit XML from CI"**
```bash
tuskr run import-junit --run-id <RUN_ID> --project-id <ID> --file <FILE.xml>
```

**"Add test results"** — results.json must be an array: `[{"testCase": "<ID>", "status": "passed"}, ...]`
```bash
tuskr run add-results --run-id <RUN_ID> --file results.json
```

**"List test suites"**
```bash
tuskr suite list --project-id <ID> --json
```

## Output parsing

Always use `--json` when you need to extract an ID for a follow-up command.
All list responses return `data.rows` (array) and `data.count` (total).

Key fields per entity:
- project: `id`, `name`, `status`
- test-case: `id`, `name`, `project`
- test-run: `id`, `name`, `status`, `project`
- result: `id`, `testCase`, `status`
- suite: `id`, `name`, `project`

## Full command reference

```
tuskr config set --token TOKEN --tenant-id TENANT_ID
tuskr config show | validate

tuskr project list [--limit N] [--offset N] [--json]
tuskr project create --name NAME [--description D] [--json]

tuskr case list [--project-id ID] [--limit N] [--offset N] [--json]
tuskr case create --name NAME --project-id ID [--json]
tuskr case upsert --file FILE.json [--json]
tuskr case import --file FILE.json [--json]

tuskr run list [--project-id ID] [--limit N] [--json]
tuskr run create --name NAME --project-id ID [--json]
tuskr run results RUN_ID [--status passed|failed|untested] [--limit N] [--json]
tuskr run add-results --run-id RUN_ID --file FILE.json [--json]
tuskr run import-junit --run-id RUN_ID --project-id ID --file FILE.xml [--json]

tuskr suite list [--project-id ID] [--json]
```
