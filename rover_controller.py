# rover_controller.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Pose:
    x: float | None = None
    y: float | None = None
    z: float | None = None
    yaw: float | None = None


def get_pose(robot: Any) -> Pose:
    """Read current pose using Cyberwave twin internals that exist on this class."""
    pos = None
    rot = None

    if hasattr(robot, "_get_current_position") and callable(getattr(robot, "_get_current_position")):
        try:
            pos = robot._get_current_position()
        except Exception:
            pos = None
    if hasattr(robot, "_get_current_rotation") and callable(getattr(robot, "_get_current_rotation")):
        try:
            rot = robot._get_current_rotation()
        except Exception:
            rot = None

    if pos is None and hasattr(robot, "_position"):
        pos = getattr(robot, "_position", None)
    if rot is None and hasattr(robot, "_rotation"):
        rot = getattr(robot, "_rotation", None)

    def _xyz(v: Any):
        if v is None:
            return (None, None, None)
        if isinstance(v, dict):
            return (v.get("x"), v.get("y"), v.get("z"))
        if all(hasattr(v, a) for a in ("x", "y", "z")):
            return (getattr(v, "x"), getattr(v, "y"), getattr(v, "z"))
        if isinstance(v, (list, tuple)) and len(v) >= 3:
            return (v[0], v[1], v[2])
        return (None, None, None)

    x, y, z = _xyz(pos)

    yaw = None
    if rot is not None:
        if isinstance(rot, dict):
            yaw = rot.get("yaw") or rot.get("z")
        elif hasattr(rot, "yaw"):
            yaw = getattr(rot, "yaw")
        elif isinstance(rot, (list, tuple)) and len(rot) == 3:
            yaw = rot[2]

    return Pose(x=x, y=y, z=z, yaw=yaw)


def move_forward(robot: Any, meters: float) -> None:
    """
    Primary mobility primitive: move forward by meters.
    Requires twin exposing move_forward().
    """
    if not hasattr(robot, "move_forward") or not callable(getattr(robot, "move_forward")):
        raise RuntimeError("This twin does not support move_forward().")
    print(f"Using robot.move_forward({meters})")
    robot.move_forward(meters)


def move_to(robot: Any, x: float, y: float, z: float) -> None:
    """
    Secondary: move to world position if supported.
    Note: this is different from edit_position (editor pose). Prefer move_to if you want 'go to coordinate'.
    """
    if hasattr(robot, "move") and callable(getattr(robot, "move")):
        print(f"Using robot.move({x},{y},{z})")
        robot.move(x, y, z)
        return
    raise RuntimeError("This twin does not support move(x,y,z).")


def capture_frame(robot: Any):
    """
    Return the latest camera frame if available.
    We'll wire this into app.py next.
    """
    if hasattr(robot, "get_latest_frame") and callable(getattr(robot, "get_latest_frame")):
        return robot.get_latest_frame()
    if hasattr(robot, "capture_frame") and callable(getattr(robot, "capture_frame")):
        return robot.capture_frame()
    raise RuntimeError("No camera frame method found (get_latest_frame/capture_frame).")