# app.py
from __future__ import annotations

import argparse
import sys
from typing import Any

from config import load_settings, debug_print_settings
from cyberwave_client import connect_twin, get_twin_info, print_twin_info


def _try_move(robot: Any, x: float, y: float, z: float) -> None:
    """
    Move the twin in the digital environment (safe test).
    We do NOT assume this moves the physical robot.
    """

    # Prefer robot.move(x,y,z) if available (twin pose move)
    if hasattr(robot, "move") and callable(getattr(robot, "move")):
        print("Using robot.move(x,y,z)")
        robot.move(x, y, z)
        return

    # Fallback: edit_position(x=...,y=...,z=...)
    if hasattr(robot, "edit_position") and callable(getattr(robot, "edit_position")):
        print("Using robot.edit_position(x=..., y=..., z=...)")
        robot.edit_position(x=x, y=y, z=z)
        return

    raise RuntimeError("No supported move method found (expected move() or edit_position()).")


def cmd_info() -> int:
    s = load_settings()
    debug_print_settings(s)

    robot = connect_twin(s)
    info = get_twin_info(robot, s)
    print_twin_info(info)
    return 0


def cmd_move(x: float, y: float, z: float) -> int:
    s = load_settings()
    debug_print_settings(s)

    if s.dry_run:
        print(f"[DRY_RUN] Would move twin to x={x}, y={y}, z={z}")
        return 0

    robot = connect_twin(s)
    _try_move(robot, x, y, z)
    print("Move command sent.")
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
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cyberwave-ugv-connector")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("info", help="Print connected twin info and capability hints")

    sub.add_parser("schema", help="Print robot.get_schema() to discover available commands/capabilities")

    pm = sub.add_parser("move", help="Move the digital twin to x,y,z (simulation pose move)")
    pm.add_argument("--x", type=float, required=True)
    pm.add_argument("--y", type=float, required=True)
    pm.add_argument("--z", type=float, required=True)

    return p


def main(argv: list[str]) -> int:
    p = build_parser()
    args = p.parse_args(argv)

    if args.cmd == "info":
        return cmd_info()
    if args.cmd == "move":
        return cmd_move(args.x, args.y, args.z)
    if args.cmd == "schema":
        return cmd_schema()

    print(f"Unknown command: {args.cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))