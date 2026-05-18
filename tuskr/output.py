import json
import sys
from typing import Any


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2))


def print_table(rows: list[dict], columns: list[str]) -> None:
    if not rows:
        print("(no results)")
        return
    widths = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            widths[col] = max(widths[col], len(str(row.get(col, ""))))
    header = "  ".join(col.upper().ljust(widths[col]) for col in columns)
    print(header)
    print("-" * len(header))
    for row in rows:
        print("  ".join(str(row.get(col, "")).ljust(widths[col]) for col in columns))


def print_success(msg: str) -> None:
    print(f"[ok] {msg}")


def print_error(msg: str) -> None:
    print(f"[error] {msg}", file=sys.stderr)
