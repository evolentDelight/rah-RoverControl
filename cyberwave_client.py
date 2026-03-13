# cyberwave_client.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from config import Settings


@dataclass
class TwinInfo:
    asset: str
    twin_uuid: str
    environment_id: str
    twin_type: str
    methods: list[str]


def _filter_methods(obj: Any) -> list[str]:
    keys = [
        "move", "forward", "back", "turn", "drive", "vel", "cmd", "teleop", "twist",
        "edit_", "position", "rotation",
        "camera", "frame", "stream", "video",
        "schema", "subscribe", "state", "pose", "odom", "imu", "lidar", "depth",
        "joint",
    ]
    out: list[str] = []
    for m in dir(obj):
        ml = m.lower()
        if any(k in ml for k in keys):
            out.append(m)
    return sorted(out)


def connect_twin(settings: Settings) -> Any:
    """
    Official pattern:

        from cyberwave import Cyberwave
        cw = Cyberwave()
        robot = cw.twin(asset, twin_id=..., environment_id=...)
    """
    # Ensure the SDK can see auth in env if it expects it
    # (safe even if unused)
    import os
    if settings.cyberwave_api_key:
        os.environ["CYBERWAVE_API_KEY"] = settings.cyberwave_api_key
    if settings.cyberwave_token:
        os.environ["CYBERWAVE_TOKEN"] = settings.cyberwave_token

    try:
        from cyberwave import Cyberwave  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "Failed to import Cyberwave from 'cyberwave'.\n"
            "Make sure cyberwave is installed in your venv.\n"
            f"Original error: {e}"
        ) from e

    cw = Cyberwave()

    try:
        robot = cw.twin(
            settings.cyberwave_asset,
            twin_id=settings.cyberwave_twin_uuid,
            environment_id=settings.cyberwave_environment_id,
        )
    except TypeError as e:
        # This is where the 'multiple values for environment_id' issue can happen.
        raise RuntimeError(
            "Cyberwave().twin(...) raised a TypeError.\n"
            "If it mentions multiple values for environment_id, you likely have an env/config "
            "also setting environment_id. Try unsetting any ENVIRONMENT_ID/CYBERWAVE_ENVIRONMENT_ID "
            "exported vars and rely on the .env + this call.\n"
            f"Original error: {e}"
        ) from e
    except Exception as e:
        raise RuntimeError(
            "Failed to connect using Cyberwave().twin(asset, twin_id=..., environment_id=...).\n"
            f"asset={settings.cyberwave_asset}\n"
            f"twin_id={settings.cyberwave_twin_uuid}\n"
            f"environment_id={settings.cyberwave_environment_id}\n"
            f"Original error: {e}"
        ) from e

    return robot


def get_twin_info(robot: Any, settings: Settings) -> TwinInfo:
    return TwinInfo(
        asset=settings.cyberwave_asset,
        twin_uuid=settings.cyberwave_twin_uuid,
        environment_id=settings.cyberwave_environment_id,
        twin_type=str(type(robot)),
        methods=_filter_methods(robot),
    )


def print_twin_info(info: TwinInfo) -> None:
    print("=== Cyberwave Twin Connected ===")
    print("asset:", info.asset)
    print("twin_uuid:", info.twin_uuid)
    print("environment_id:", info.environment_id)
    print("type:", info.twin_type)
    print("filtered methods:")
    for m in info.methods:
        print(" -", m)