import json
import sys

import click

from .client import TuskrAPIError, TuskrClient
from .config import ConfigError, load_config, mask_token, save_config
from .output import print_error, print_json, print_success, print_table


def _client() -> TuskrClient:
    try:
        return TuskrClient(load_config())
    except ConfigError as e:
        print_error(str(e))
        sys.exit(1)


def _die(e: TuskrAPIError) -> None:
    print_error(str(e))
    sys.exit(1)


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------

@click.group()
def cli():
    """Tuskr test management CLI."""


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------

@cli.group()
def config():
    """Manage API credentials."""


@config.command("set")
@click.option("--token", required=True, help="Permanent API access token.")
@click.option("--tenant-id", required=True, help="Your Tuskr tenant UUID.")
def config_set(token, tenant_id):
    """Save credentials to ~/.config/tuskr/config.json."""
    save_config(token, tenant_id)
    print_success(f"Config saved (tenant: {tenant_id}, token: {mask_token(token)})")


@config.command("show")
def config_show():
    """Print current credentials (token masked)."""
    try:
        cfg = load_config()
        print(f"tenant_id : {cfg.tenant_id}")
        print(f"token     : {mask_token(cfg.token)}")
    except ConfigError as e:
        print_error(str(e))
        sys.exit(1)


@config.command("validate")
def config_validate():
    """Verify credentials by listing projects."""
    client = _client()
    try:
        result = client.get("/project", params={"limit": 1})
        count = result.get("data", {}).get("count", "?")
        print_success(f"Credentials valid. {count} project(s) found.")
    except TuskrAPIError as e:
        _die(e)


# ---------------------------------------------------------------------------
# project
# ---------------------------------------------------------------------------

@cli.group()
def project():
    """Manage projects."""


@project.command("list")
@click.option("--limit", default=20, show_default=True)
@click.option("--offset", default=0, show_default=True)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def project_list(limit, offset, as_json):
    """List projects. [GET /project]"""
    client = _client()
    try:
        result = client.get("/project", params={"limit": limit, "offset": offset})
    except TuskrAPIError as e:
        _die(e)
    if as_json:
        print_json(result)
    else:
        rows = result.get("data", {}).get("rows", [])
        print_table(rows, ["id", "name", "status"])


@project.command("create")
@click.option("--name", required=True)
@click.option("--description", default="")
@click.option("--json", "as_json", is_flag=True)
def project_create(name, description, as_json):
    """Create a project. [POST /project]"""
    client = _client()
    payload = {"name": name}
    if description:
        payload["description"] = description
    try:
        result = client.post("/project", payload)
    except TuskrAPIError as e:
        _die(e)
    if as_json:
        print_json(result)
    else:
        data = result.get("data", {})
        print_success(f"Created project '{data.get('name')}' (id: {data.get('id')})")


# ---------------------------------------------------------------------------
# case (test cases)
# ---------------------------------------------------------------------------

@cli.group()
def case():
    """Manage test cases."""


@case.command("list")
@click.option("--project-id")
@click.option("--limit", default=20, show_default=True)
@click.option("--offset", default=0, show_default=True)
@click.option("--json", "as_json", is_flag=True)
def case_list(project_id, limit, offset, as_json):
    """List test cases. [GET /test-case]"""
    client = _client()
    params = {"limit": limit, "offset": offset}
    if project_id:
        params["project"] = project_id
    try:
        result = client.get("/test-case", params=params)
    except TuskrAPIError as e:
        _die(e)
    if as_json:
        print_json(result)
    else:
        rows = result.get("data", {}).get("rows", [])
        print_table(rows, ["id", "name", "project"])


@case.command("create")
@click.option("--name", required=True)
@click.option("--project-id", required=True)
@click.option("--json", "as_json", is_flag=True)
def case_create(name, project_id, as_json):
    """Create a test case. [POST /test-case]"""
    client = _client()
    try:
        result = client.post("/test-case", {"name": name, "project": project_id})
    except TuskrAPIError as e:
        _die(e)
    if as_json:
        print_json(result)
    else:
        data = result.get("data", {})
        print_success(f"Created test case '{data.get('name')}' (id: {data.get('id')})")


@case.command("upsert")
@click.option("--file", "file_path", required=True, type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True)
def case_upsert(file_path, as_json):
    """Upsert a test case from a JSON file. [POST /test-case/upsert]"""
    client = _client()
    with open(file_path) as f:
        payload = json.load(f)
    try:
        result = client.post("/test-case/upsert", payload)
    except TuskrAPIError as e:
        _die(e)
    if as_json:
        print_json(result)
    else:
        print_success("Upsert complete.")
        if result.get("data", {}).get("rowsWithErrors"):
            print_error(f"Rows with errors: {result['data']['rowsWithErrors']}")


@case.command("import")
@click.option("--file", "file_path", required=True, type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True)
def case_import(file_path, as_json):
    """Bulk import test cases from a JSON file. [POST /test-case/import]"""
    client = _client()
    with open(file_path) as f:
        payload = json.load(f)
    try:
        result = client.post("/test-case/import", payload)
    except TuskrAPIError as e:
        _die(e)
    if as_json:
        print_json(result)
    else:
        data = result.get("data", {})
        print_success(f"Imported. Rows with errors: {len(data.get('rowsWithErrors', []))}")


# ---------------------------------------------------------------------------
# run (test runs)
# ---------------------------------------------------------------------------

@cli.group()
def run():
    """Manage test runs."""


@run.command("list")
@click.option("--project-id")
@click.option("--limit", default=20, show_default=True)
@click.option("--offset", default=0, show_default=True)
@click.option("--json", "as_json", is_flag=True)
def run_list(project_id, limit, offset, as_json):
    """List test runs. [GET /test-run]"""
    client = _client()
    params = {"limit": limit, "offset": offset}
    if project_id:
        params["project"] = project_id
    try:
        result = client.get("/test-run", params=params)
    except TuskrAPIError as e:
        _die(e)
    if as_json:
        print_json(result)
    else:
        rows = result.get("data", {}).get("rows", [])
        print_table(rows, ["id", "name", "status", "project"])


@run.command("create")
@click.option("--name", required=True)
@click.option("--project-id", required=True)
@click.option("--all-cases", is_flag=True, default=True, help="Include all test cases.")
@click.option("--json", "as_json", is_flag=True)
def run_create(name, project_id, all_cases, as_json):
    """Create a test run. [POST /test-run]"""
    client = _client()
    payload = {
        "name": name,
        "project": project_id,
        "testCaseInclusionType": "ALL" if all_cases else "SPECIFIC",
    }
    try:
        result = client.post("/test-run", payload)
    except TuskrAPIError as e:
        _die(e)
    if as_json:
        print_json(result)
    else:
        data = result.get("data", {})
        print_success(f"Created run '{data.get('name')}' (id: {data.get('id')})")


@run.command("results")
@click.argument("run_id")
@click.option("--status", help="Filter by status (e.g. passed, failed, untested).")
@click.option("--limit", default=50, show_default=True)
@click.option("--offset", default=0, show_default=True)
@click.option("--json", "as_json", is_flag=True)
def run_results(run_id, status, limit, offset, as_json):
    """Get results for a test run. [GET /test-run/<id>/results]"""
    client = _client()
    params = {"limit": limit, "offset": offset}
    if status:
        params["status"] = status
    try:
        result = client.get(f"/test-run/{run_id}/results", params=params)
    except TuskrAPIError as e:
        _die(e)
    if as_json:
        print_json(result)
    else:
        rows = result.get("data", {}).get("rows", [])
        print_table(rows, ["id", "testCase", "status", "assignedTo"])


@run.command("add-results")
@click.option("--run-id", required=True)
@click.option("--file", "file_path", required=True, type=click.Path(exists=True),
              help="JSON file with array of result objects.")
@click.option("--json", "as_json", is_flag=True)
def run_add_results(run_id, file_path, as_json):
    """Bulk-add test results. [POST /test-run-result/bulk]"""
    client = _client()
    with open(file_path) as f:
        results_data = json.load(f)
    payload = {"testRun": run_id, "results": results_data}
    try:
        result = client.post("/test-run-result/bulk", payload)
    except TuskrAPIError as e:
        _die(e)
    if as_json:
        print_json(result)
    else:
        print_success("Results added.")


@run.command("import-junit")
@click.option("--run-id", required=True)
@click.option("--file", "file_path", required=True, type=click.Path(exists=True),
              help="JUnit XML file.")
@click.option("--project-id", required=True)
@click.option("--json", "as_json", is_flag=True)
def run_import_junit(run_id, file_path, project_id, as_json):
    """Import test results from JUnit XML. [POST /test-run/import-junit-xml]"""
    client = _client()
    with open(file_path, "rb") as f:
        try:
            result = client.post_raw(
                "/test-run/import-junit-xml",
                files={
                    "file": f,
                    "testRun": (None, run_id),
                    "project": (None, project_id),
                },
            )
        except TuskrAPIError as e:
            _die(e)
    if as_json:
        print_json(result)
    else:
        print_success("JUnit XML imported.")


# ---------------------------------------------------------------------------
# suite (test suites)
# ---------------------------------------------------------------------------

@cli.group()
def suite():
    """List test suites."""


@suite.command("list")
@click.option("--project-id")
@click.option("--json", "as_json", is_flag=True)
def suite_list(project_id, as_json):
    """List test suites and sections. [GET /test-suite]"""
    client = _client()
    params = {}
    if project_id:
        params["project"] = project_id
    try:
        result = client.get("/test-suite", params=params or None)
    except TuskrAPIError as e:
        _die(e)
    if as_json:
        print_json(result)
    else:
        rows = result.get("data", {}).get("rows", [])
        print_table(rows, ["id", "name", "project"])
