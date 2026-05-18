# tuskr-cli — Agent Guide

Python CLI for the [Tuskr](https://tuskr.app) test management API, published as `tuskr-cli` on PyPI.

## Setup

```bash
pip install -e .
tuskr config set --token YOUR_TOKEN --tenant-id YOUR_TENANT_ID
tuskr config validate
```

Credentials are stored at `~/.config/tuskr/config.json`.

## Code Structure

| File | Purpose |
|------|---------|
| `tuskr/cli.py` | Click command groups: `config` / `project` / `case` / `run` / `suite` |
| `tuskr/client.py` | HTTP client — rate limiting, response handling, `paginate()` utility |
| `tuskr/config.py` | Load/save credentials; `Config` dataclass; `mask_token()` helper |
| `tuskr/output.py` | `print_table`, `print_json`, `print_success`, `print_error` |
| `plugins/tuskr-skill/skills/tuskr/SKILL.md` | Claude Code skill definition — update when commands change |

## API Conventions

These are critical — getting them wrong causes HTTP 400 errors:

- **Project filter**: use `filter[project]=<id>` (not `project=`) for `test-case`, `test-run`, and `test-suite` endpoints
- **Pagination**: use `page=N` (100 records/page) for those endpoints; `project` list uses `limit`/`offset`
- **Response format**: `{rows: [], count: N, meta: {total, pages}}` at the top level — no `data` wrapper
- **POST bodies**: `client.post()` wraps payload as `{"data": payload}` automatically

## Adding a New Command

1. Add a `@<group>.command(...)` function in `tuskr/cli.py`
2. Use `client.get()` / `client.post()` from `tuskr/client.py`
3. Parse response with `result.get("rows", [])` for lists, `result.get("data", {})` for POST responses
4. Use `print_table()` for default output, `print_json(result)` when `--json` flag is set

## Build & Publish

```bash
python3 -m build
python3 -m twine upload dist/*
```

Before publishing:
- Bump `version` in `pyproject.toml`
- Keep `__version__` in `tuskr/__init__.py` in sync

## Tests

No automated test suite exists yet. Validate manually with `tuskr config validate` and live API calls.

## API Reference

https://tuskr.app/kb/latest/api
