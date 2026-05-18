# Tuskr Claude Code Plugin Marketplace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the tuskr skill as a Claude Code plugin marketplace in the `harish-talview/tuskr-cli` GitHub repo so users can add it via `/plugin marketplace add harish-talview/tuskr-cli` and install via `/plugin install tuskr-skill@tuskr`.

**Architecture:** The `tuskr-cli` repo becomes a plugin marketplace by adding a `.claude-plugin/marketplace.json` catalog at its root. The actual skill lives in `plugins/tuskr-skill/` as a self-contained plugin directory with its own `plugin.json` manifest and a `skills/tuskr/SKILL.md` written as Claude instructions (not user docs — this is what Claude reads when the skill is active).

**Tech Stack:** JSON (marketplace/plugin manifests), Markdown with YAML frontmatter (SKILL.md), Git/GitHub hosting.

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `.claude-plugin/marketplace.json` | Marketplace catalog — lists available plugins, metadata, owner |
| Create | `plugins/tuskr-skill/.claude-plugin/plugin.json` | Plugin manifest — name, version, description |
| Create | `plugins/tuskr-skill/skills/tuskr/SKILL.md` | Claude instructions for using the tuskr CLI |
| Modify | `README.md` | Add "Claude Code Plugin" section with install instructions |

---

## SKILL.md Content Specification

The Claude Code plugin SKILL.md format differs from `vercel-labs/skills`:
- `description`: ONE short line shown in plugin listings
- NO `name` field — the skill name comes from the directory (`skills/tuskr/` → name is `tuskr`)
- NO `trigger` field
- Body: **instructions written for Claude**, not for human readers

The body tells Claude what to do when this skill is active. It should cover:
1. Prerequisite check (verify CLI + config)
2. Key commands Claude should run for common intents
3. Output parsing guidance (use `--json`, extract `data.rows[].id`)

---

### Task 1: Create the marketplace catalog

**Files:**
- Create: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Create the `.claude-plugin/` directory and write `marketplace.json`**

```json
{
  "$schema": "https://claude.ai/schemas/marketplace.json",
  "name": "tuskr",
  "description": "Claude Code plugins for Tuskr test management",
  "owner": {
    "name": "Harish Gnanasekar",
    "email": "harish.gnanasekar@talview.com"
  },
  "metadata": {
    "pluginRoot": "./plugins"
  },
  "plugins": [
    {
      "name": "tuskr-skill",
      "source": "./tuskr-skill",
      "description": "Interact with the Tuskr test management API via tuskr-cli",
      "version": "1.0.0",
      "author": {
        "name": "Harish Gnanasekar",
        "email": "harish.gnanasekar@talview.com"
      },
      "homepage": "https://github.com/harish-talview/tuskr-cli",
      "repository": "https://github.com/harish-talview/tuskr-cli",
      "license": "MIT",
      "keywords": ["tuskr", "test-management", "testing", "qa"]
    }
  ]
}
```

Note: `metadata.pluginRoot` is set to `"./plugins"` so `source: "./tuskr-skill"` resolves to `./plugins/tuskr-skill`.

- [ ] **Step 2: Verify JSON is valid**

```bash
python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('valid')"
```

Expected output: `valid`

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "feat: add Claude Code plugin marketplace catalog"
```

---

### Task 2: Create the plugin manifest

**Files:**
- Create: `plugins/tuskr-skill/.claude-plugin/plugin.json`

- [ ] **Step 1: Create plugin directory and write `plugin.json`**

```bash
mkdir -p plugins/tuskr-skill/.claude-plugin
```

```json
{
  "name": "tuskr-skill",
  "description": "Interact with the Tuskr test management API via tuskr-cli",
  "version": "1.0.0"
}
```

Save to `plugins/tuskr-skill/.claude-plugin/plugin.json`.

- [ ] **Step 2: Verify JSON is valid**

```bash
python3 -c "import json; json.load(open('plugins/tuskr-skill/.claude-plugin/plugin.json')); print('valid')"
```

Expected output: `valid`

- [ ] **Step 3: Commit**

```bash
git add plugins/tuskr-skill/.claude-plugin/plugin.json
git commit -m "feat: add tuskr-skill plugin manifest"
```

---

### Task 3: Write the SKILL.md in Claude Code plugin format

**Files:**
- Create: `plugins/tuskr-skill/skills/tuskr/SKILL.md`

- [ ] **Step 1: Create skill directory**

```bash
mkdir -p plugins/tuskr-skill/skills/tuskr
```

- [ ] **Step 2: Write `SKILL.md`**

The body is written as instructions **to Claude**, not documentation for users.

```markdown
---
description: Interact with the Tuskr test management API via the tuskr CLI
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
```

- [ ] **Step 3: Commit**

```bash
git add plugins/tuskr-skill/skills/tuskr/SKILL.md
git commit -m "feat: add tuskr SKILL.md for Claude Code plugin"
```

---

### Task 4: Update README.md with plugin marketplace installation instructions

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add a "Claude Code Plugin" section to README.md**

Add this section after the existing "Install" section:

```markdown
## Claude Code Plugin

Install the tuskr skill directly into Claude Code via the plugin marketplace:

```
/plugin marketplace add harish-talview/tuskr-cli
/plugin install tuskr-skill@tuskr
```

Once installed, Claude Code will use the tuskr skill automatically when you ask about Tuskr test management. You can also invoke it directly:

```
/tuskr-skill:tuskr
```
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add Claude Code plugin marketplace installation instructions"
```

---

### Task 5: Push and verify end-to-end

- [ ] **Step 1: Push all commits to GitHub**

```bash
git push
```

- [ ] **Step 2: Verify the marketplace is discoverable**

In a Claude Code session, run:
```
/plugin marketplace add harish-talview/tuskr-cli
```

Expected: Claude Code confirms marketplace `tuskr` was added.

- [ ] **Step 3: Verify the plugin installs**

```
/plugin install tuskr-skill@tuskr
```

Expected: Claude Code confirms `tuskr-skill` was installed.

- [ ] **Step 4: Verify the skill is active**

Ask Claude: "List my Tuskr projects" — Claude should automatically run `tuskr project list --json`.

Or invoke explicitly:
```
/tuskr-skill:tuskr
```

---

## Summary

After this plan:
- `harish-talview/tuskr-cli` is a Claude Code plugin marketplace
- Users add it with one command: `/plugin marketplace add harish-talview/tuskr-cli`
- The tuskr skill is installed into Claude Code and loaded contextually when helping with Tuskr
- The SKILL.md in `plugins/tuskr-skill/skills/tuskr/` is the authoritative Claude instructions file (replaces the old `~/.claude/skills/tuskr/SKILL.md` approach for distribution)
