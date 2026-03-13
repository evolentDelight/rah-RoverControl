# app.py
from __future__ import annotations

import argparse
import sys
import time
from typing import Any

from config import load_settings, debug_print_settings
from cyberwave_client import connect_twin, get_twin_info, print_twin_info

from rover_controller import get_pose, move_forward  # expects your File 4 rover_controller.py


def _enable_telemetry_best_effort(robot: Any) -> None:
    """
    Many Cyberwave twins populate pose via subscription callbacks.
    We subscribe with a no-op callback to activate updates.
    Safe no-op if methods don't exist.
    """
    try:
        if hasattr(robot, "subscribe_position") and callable(getattr(robot, "subscribe_position")):
            robot.subscribe_position(lambda _: None)
        if hasattr(robot, "subscribe_rotation") and callable(getattr(robot, "subscribe_rotation")):
            robot.subscribe_rotation(lambda _: None)
    except Exception:
        # Telemetry is optional; don't fail commands if subscribe fails.
        pass


def cmd_info() -> int:
    s = load_settings()
    debug_print_settings(s)

    robot = connect_twin(s)
    info = get_twin_info(robot, s)
    print_twin_info(info)
    return 0


def cmd_schema() -> int:
    s = load_settings()
    debug_print_settings(s)

    robot = connect_twin(s)

    if not hasattr(robot, "get_schema") or not callable(getattr(robot, "get_schema")):
        print("This twin does not support get_schema().")
        return 1

    schema = robot.get_schema()
    print("=== get_schema() ===")
    print(schema)

    # Small locomotion summary (if present)
    try:
        caps = schema.get("extensions", {}).get("cyberwave", {}).get("capabilities", {})
        locomotion = caps.get("locomotion", {})
        print("\n=== Locomotion summary ===")
        for k in ["mode", "has_wheels", "has_legs", "max_linear_velocity", "max_angular_velocity"]:
            print(f"{k}: {locomotion.get(k)}")
        print("asset_registry_id:", schema.get("extensions", {}).get("cyberwave", {}).get("asset_registry_id"))
    except Exception:
        pass

    return 0


def cmd_pose(wait_s: float) -> int:
    s = load_settings()
    debug_print_settings(s)

    robot = connect_twin(s)
    _enable_telemetry_best_effort(robot)

    if wait_s > 0:
        time.sleep(wait_s)

    print("pose:", get_pose(robot))
    return 0


def cmd_forward(meters: float, pose_wait_s: float) -> int:
    s = load_settings()
    debug_print_settings(s)

    if s.dry_run:
        print(f"[DRY_RUN] Would move forward {meters} meters")
        return 0

    robot = connect_twin(s)
    _enable_telemetry_best_effort(robot)

    print(f"Sending move_forward({meters}). If nothing moves, make sure the Cyberwave UI has Simulate ON.")
    move_forward(robot, meters)
    print("Forward command sent.")

    # Optional: wait briefly then print pose
    if pose_wait_s > 0:
        time.sleep(pose_wait_s)
        print("pose after:", get_pose(robot))

    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cyberwave-ugv-connector")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("info", help="Print connected twin info and capability hints")
    sub.add_parser("schema", help="Print robot.get_schema() and locomotion summary")

    pp = sub.add_parser("pose", help="Print current pose (best-effort; may require sim running)")
    pp.add_argument("--wait", type=float, default=0.0, help="Seconds to wait before reading pose (default 0)")

    pf = sub.add_parser("forward", help="Move forward by N meters (requires simulation running)")
    pf.add_argument("--meters", type=float, required=True)
    pf.add_argument("--pose-wait", type=float, default=0.8, help="Seconds to wait then print pose (default 0.8)")

    return p


def main(argv: list[str]) -> int:
    p = build_parser()
    args = p.parse_args(argv)

    if args.cmd == "info":
        return cmd_info()
    if args.cmd == "schema":
        return cmd_schema()
    if args.cmd == "pose":
        return cmd_pose(wait_s=args.wait)
    if args.cmd == "forward":
        return cmd_forward(meters=args.meters, pose_wait_s=args.pose_wait)

    print(f"Unknown command: {args.cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))