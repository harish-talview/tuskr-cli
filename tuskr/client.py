import time
from typing import Any

import requests

from .config import Config


class TuskrAPIError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"HTTP {status}: {message}")


class TuskrClient:
    def __init__(self, config: Config):
        self._config = config
        self._base = f"https://api.tuskr.live/api/tenant/{config.tenant_id}"
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {config.token}",
            "Content-Type": "application/json",
        })

    def _url(self, path: str) -> str:
        return self._base + path

    def _check_rate_limit(self, resp: requests.Response) -> None:
        remaining = int(resp.headers.get("X-RateLimit-Remaining", 1))
        if remaining == 0:
            reset_at = int(resp.headers.get("X-RateLimit-Reset", 0))
            sleep_for = max(0.0, reset_at - time.time()) + 0.1
            time.sleep(sleep_for)

    def _handle(self, resp: requests.Response) -> Any:
        self._check_rate_limit(resp)
        if not resp.ok:
            try:
                msg = resp.json().get("message") or resp.text
            except Exception:
                msg = resp.text
            raise TuskrAPIError(resp.status_code, msg)
        return resp.json()

    def get(self, path: str, params: dict | None = None) -> Any:
        resp = self._session.get(self._url(path), params=params)
        return self._handle(resp)

    def post(self, path: str, payload: dict) -> Any:
        resp = self._session.post(self._url(path), json={"data": payload})
        return self._handle(resp)

    def post_raw(self, path: str, files: dict) -> Any:
        """POST with multipart/form-data (e.g. JUnit XML upload)."""
        headers = {"Authorization": f"Bearer {self._config.token}"}
        resp = requests.post(self._url(path), files=files, headers=headers)
        return self._handle(resp)

    def delete(self, path: str, payload: dict | None = None) -> Any:
        resp = self._session.delete(
            self._url(path),
            json={"data": payload} if payload else None,
        )
        return self._handle(resp)

    def paginate(self, path: str, params: dict | None = None, limit: int = 50) -> list:
        params = dict(params or {})
        params["limit"] = limit
        params["offset"] = 0
        all_rows: list = []
        while True:
            result = self.get(path, params)
            data = result.get("data", {})
            rows = data.get("rows", [])
            all_rows.extend(rows)
            total = data.get("count", 0)
            if len(all_rows) >= total or not rows:
                break
            params["offset"] += limit
        return all_rows
