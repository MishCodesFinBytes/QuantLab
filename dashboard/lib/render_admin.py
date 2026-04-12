"""Render REST API client for recreating the free-tier Postgres.

Free Render Postgres expires 90 days after creation. This module lets the
admin page delete the old DB, create a fresh one with the same name, rewire
the web service's DATABASE_URL env var, and trigger a redeploy — in one click.

Required Streamlit secrets (in [render] table):
    api_key          Render personal API token (rnd_...)
    owner_id         Render owner id (tea_... or usr_...)
    postgres_id      Current Postgres instance id (dpg-...)
    service_id       Web service id to update (srv-...)
    db_name          Name to reuse for the new Postgres
    plan             'free' (default)
    region           'oregon' (default)
    env_var_key      'DATABASE_URL' (default)
    url_scheme       Target URL scheme (default 'postgresql+asyncpg')
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests

API_BASE = "https://api.render.com/v1"


@dataclass
class RenderConfig:
    api_key: str
    owner_id: str
    postgres_id: str
    service_id: str
    db_name: str
    plan: str = "free"
    region: str = "oregon"
    env_var_key: str = "DATABASE_URL"
    url_scheme: str = "postgresql+asyncpg"


class RenderError(Exception):
    pass


class RenderClient:
    def __init__(self, cfg: RenderConfig):
        self.cfg = cfg
        self.s = requests.Session()
        self.s.headers.update({
            "Authorization": f"Bearer {cfg.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    def _req(self, method: str, path: str, **kw) -> Any:
        r = self.s.request(method, f"{API_BASE}{path}", timeout=30, **kw)
        if not r.ok:
            raise RenderError(f"{method} {path} -> {r.status_code}: {r.text[:300]}")
        return r.json() if r.text else {}

    # --- Postgres --------------------------------------------------------

    def get_postgres(self, pid: str) -> dict:
        return self._req("GET", f"/postgres/{pid}")

    def delete_postgres(self, pid: str) -> None:
        self._req("DELETE", f"/postgres/{pid}")

    def create_postgres(self) -> dict:
        payload = {
            "name": self.cfg.db_name,
            "plan": self.cfg.plan,
            "region": self.cfg.region,
            "ownerId": self.cfg.owner_id,
            "version": "16",
        }
        return self._req("POST", "/postgres", json=payload)

    def wait_postgres_available(self, pid: str, timeout: int = 600, poll: int = 5) -> dict:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            info = self.get_postgres(pid)
            if info.get("status") == "available":
                return info
            time.sleep(poll)
        raise RenderError(f"Postgres {pid} not available after {timeout}s")

    def internal_url(self, pid: str) -> str:
        info = self._req("GET", f"/postgres/{pid}/connection-info")
        url = info.get("internalConnectionString") or info.get("externalConnectionString")
        if not url:
            raise RenderError(f"No connection string for {pid}")
        return url

    # --- Service env vars -----------------------------------------------

    def list_env_vars(self) -> list[dict]:
        data = self._req("GET", f"/services/{self.cfg.service_id}/env-vars")
        if isinstance(data, list):
            return [row.get("envVar", row) for row in data]
        return []

    def put_env_vars(self, items: list[dict]) -> None:
        self._req("PUT", f"/services/{self.cfg.service_id}/env-vars", json=items)

    def set_env_var(self, key: str, value: str) -> None:
        items = self.list_env_vars()
        found = False
        for it in items:
            if it.get("key") == key:
                it["value"] = value
                found = True
        if not found:
            items.append({"key": key, "value": value})
        self.put_env_vars([{"key": it["key"], "value": it["value"]} for it in items])

    # --- Deploy ----------------------------------------------------------

    def trigger_deploy(self) -> dict:
        return self._req("POST", f"/services/{self.cfg.service_id}/deploys", json={})


def rewrite_scheme(url: str, new_scheme: str) -> str:
    if "://" not in url:
        raise ValueError(f"Not a URL: {url!r}")
    _, rest = url.split("://", 1)
    return f"{new_scheme}://{rest}"
