import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "tuskr" / "config.json"


class ConfigError(RuntimeError):
    pass


class Config:
    def __init__(self, token: str, tenant_id: str):
        self.token = token
        self.tenant_id = tenant_id


def load_config() -> Config:
    if not CONFIG_PATH.exists():
        raise ConfigError(
            "Tuskr is not configured. Run:\n"
            "  tuskr config set --token TOKEN --tenant-id TENANT_ID"
        )
    try:
        data = json.loads(CONFIG_PATH.read_text())
        return Config(token=data["token"], tenant_id=data["tenant_id"])
    except (KeyError, json.JSONDecodeError) as e:
        raise ConfigError(f"Config file is invalid ({e}). Run: tuskr config set") from e


def save_config(token: str, tenant_id: str) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = CONFIG_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps({"token": token, "tenant_id": tenant_id}, indent=2))
    tmp.replace(CONFIG_PATH)


def mask_token(token: str) -> str:
    if len(token) <= 8:
        return "****"
    return token[:4] + "****" + token[-4:]
