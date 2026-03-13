from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load .env from current working directory, overriding any exported vars
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"), override=True)


def _get_env(name: str, default: str | None = None) -> str | None:
    val = os.getenv(name)
    if val is None:
        return default
    val = val.strip()
    return val if val else default


def _get_bool(name: str, default: bool = False) -> bool:
    v = _get_env(name)
    if v is None:
        return default
    return v.lower() in ("1", "true", "yes", "y", "on")


def _get_int(name: str, default: int) -> int:
    v = _get_env(name)
    if v is None:
        return default
    try:
        return int(v)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    # Official Cyberwave pattern parameters
    cyberwave_asset: str                  # e.g. "waveshare/ugv-beast"
    cyberwave_twin_uuid: str              # UUID string
    cyberwave_environment_id: str         # UUID string

    # Runtime
    dry_run: bool
    host: str
    port: int

    # Auth (optional: SDK may read from env directly)
    cyberwave_api_key: str | None
    cyberwave_token: str | None


def load_settings() -> Settings:
    asset = _get_env("CYBERWAVE_ASSET")
    if not asset:
        raise RuntimeError(
            "Missing CYBERWAVE_ASSET (required).\n"
            "Example:\n"
            "  CYBERWAVE_ASSET=waveshare/ugv-beast\n"
        )

    twin_uuid = _get_env("CYBERWAVE_TWIN_UUID")
    if not twin_uuid:
        raise RuntimeError(
            "Missing CYBERWAVE_TWIN_UUID (required).\n"
            "This should be the twin UUID provided by the station/UI.\n"
        )

    env_id = _get_env("CYBERWAVE_ENVIRONMENT_ID")
    if not env_id:
        raise RuntimeError(
            "Missing CYBERWAVE_ENVIRONMENT_ID (required).\n"
            "This should be the environment UUID provided by the station/UI.\n"
        )

    return Settings(
        cyberwave_asset=asset,
        cyberwave_twin_uuid=twin_uuid,
        cyberwave_environment_id=env_id,
        dry_run=_get_bool("DRY_RUN", default=False),
        host=_get_env("HOST", default="127.0.0.1") or "127.0.0.1",
        port=_get_int("PORT", default=8000),
        cyberwave_api_key=_get_env("CYBERWAVE_API_KEY"),
        cyberwave_token=_get_env("CYBERWAVE_TOKEN"),
    )


def debug_print_settings(s: Settings) -> None:
    def mask(x: str | None) -> str:
        if not x:
            return "(not set)"
        if len(x) <= 6:
            return "***"
        return x[:3] + "..." + x[-3:]

    print("=== Settings ===")
    print("CYBERWAVE_ASSET:", s.cyberwave_asset)
    print("CYBERWAVE_TWIN_UUID:", s.cyberwave_twin_uuid)
    print("CYBERWAVE_ENVIRONMENT_ID:", s.cyberwave_environment_id)
    print("DRY_RUN:", s.dry_run)
    print("HOST:", s.host)
    print("PORT:", s.port)
    print("CYBERWAVE_API_KEY:", mask(s.cyberwave_api_key))
    print("CYBERWAVE_TOKEN:", mask(s.cyberwave_token))