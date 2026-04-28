#!/usr/bin/env python3
"""
Kinematics example for elite_cs_sdk.

This script mirrors the flow of the C++ kinematics example:
1) Connect Primary port and get robot MDH parameters.
2) Connect RTSI and read current joint angles and TCP pose.
3) Load KDL kinematics plugin with ClassLoader.
4) Run FK/IK and print results.

Usage:
    python examples/example_kinematics.py --ip 127.0.0.1
"""

import argparse
from pathlib import Path
import platform
import sys

import elite_cs_sdk as cs

# New kinematics bindings may not be re-exported by elite_cs_sdk.__init__ in all builds.
# Fallback to native extension module to ensure ClassLoader/KinematicsBase availability.
try:
    import elite_cs_sdk.elite_cs_sdk_python as cs_native
except Exception:
    cs_native = cs


def _fmt_vec(vec):
    return "[" + ", ".join(f"{float(x):.6f}" for x in vec) + "]"


def _print_vec(name, vec):
    print(f"{name}: {_fmt_vec(vec)}")


def _resolve_plugin_path(plugin_path_arg):
    if plugin_path_arg:
        user_path = Path(plugin_path_arg).expanduser().resolve()
        if not user_path.exists():
            raise FileNotFoundError(f"Plugin file not found: {user_path}")
        return user_path

    module_dir = Path(cs_native.__file__).resolve().parent
    ext_map = {
        "Linux": "libelite_kdl_kinematics.so",
        "Windows": "elite_kdl_kinematics.dll",
        "Darwin": "libelite_kdl_kinematics.dylib",
    }

    expected_name = ext_map.get(platform.system())
    if expected_name:
        expected = module_dir / expected_name
        if expected.exists():
            return expected

    candidates = list(module_dir.glob("*kdl*kinematics*.so"))
    candidates += list(module_dir.glob("*kdl*kinematics*.dll"))
    candidates += list(module_dir.glob("*kdl*kinematics*.dylib"))
    if candidates:
        return candidates[0]

    raise FileNotFoundError(
        "Kinematics plugin library was not found in installed package. "
        f"Checked under: {module_dir}"
    )


def main():
    parser = argparse.ArgumentParser(description="Run kinematics FK/IK against a robot.")
    parser.add_argument("--ip", default="127.0.0.1", help="Robot IP (default: 127.0.0.1)")
    parser.add_argument("--primary-timeout-ms", type=int, default=1000, help="Primary timeout in ms")
    parser.add_argument("--rtsi-frequency", type=float, default=250.0, help="RTSI frequency")
    parser.add_argument(
        "--plugin-path",
        default="",
        help="Optional absolute path to kinematics plugin library",
    )
    args = parser.parse_args()

    print(f"[INFO] Connecting robot: {args.ip}")

    primary = cs.PrimaryClientInterface()
    if not primary.connect(args.ip):
        print(
            f"[ERROR] Failed to connect Primary port {args.ip}",
            file=sys.stderr,
        )
        return 1

    kin_info = cs.KinematicsInfo()
    try:
        if not primary.getPackage(kin_info, args.primary_timeout_ms):
            print("[ERROR] Failed to get KinematicsInfo from Primary port", file=sys.stderr)
            return 1
    finally:
        primary.disconnect()

    print("[INFO] Got robot kinematics info from Primary port")

    resource_dir = Path(__file__).resolve().parent / "resource"
    output_recipe = resource_dir / "output_recipe.txt"
    input_recipe = resource_dir / "input_recipe.txt"

    if not output_recipe.exists() or not input_recipe.exists():
        print(
            "[ERROR] RTSI recipe files are missing under examples/resource",
            file=sys.stderr,
        )
        return 1

    io = cs.RtsiIOInterface(str(output_recipe), str(input_recipe), args.rtsi_frequency)
    if not io.connect(args.ip):
        print(f"[ERROR] Failed to connect RTSI server at {args.ip}:30004", file=sys.stderr)
        return 1

    try:
        current_joint = io.getActualJointPositions()
        current_tcp = io.getActualTCPPose()
    finally:
        io.disconnect()

    print("[INFO] Got actual joint positions and TCP pose from RTSI")

    try:
        plugin_path = _resolve_plugin_path(args.plugin_path or None)
    except FileNotFoundError as ex:
        print(f"[ERROR] {ex}", file=sys.stderr)
        return 1

    print(f"[INFO] Loading kinematics plugin: {plugin_path}")

    if not hasattr(cs_native, "ClassLoader"):
        print(
            "[ERROR] Current Python package does not expose ClassLoader. "
            "Please reinstall the latest built wheel.",
            file=sys.stderr,
        )
        return 1

    loader = cs_native.ClassLoader(str(plugin_path))
    if not loader.loadLib():
        print("[ERROR] Failed to load kinematics plugin library", file=sys.stderr)
        return 1

    solver = loader.createKinematicsInstance("ELITE::KdlKinematicsPlugin")
    if solver is None:
        print("[ERROR] Failed to create ELITE::KdlKinematicsPlugin instance", file=sys.stderr)
        return 1

    solver.setMDH(kin_info.dh_alpha_, kin_info.dh_a_, kin_info.dh_d_)

    ok_fk, fk_pose = solver.getPositionFK(current_joint)
    if not ok_fk:
        print("[ERROR] FK failed", file=sys.stderr)
        return 1

    ok_ik, ik_joint, ik_result = solver.getPositionIK(current_tcp, current_joint)
    if not ok_ik:
        print(
            f"[ERROR] IK failed, error={getattr(ik_result, 'kinematic_error', 'UNKNOWN')}",
            file=sys.stderr,
        )
        return 1

    ok_ik_all, all_solutions, all_result = solver.getPositionIKAll(current_tcp, current_joint)

    _print_vec("Current TCP", current_tcp)
    _print_vec("FK Pose", fk_pose)
    _print_vec("Current Joint", current_joint)
    _print_vec("IK Joint", ik_joint)

    print(f"IK Result Error: {getattr(ik_result, 'kinematic_error', 'UNKNOWN')}")
    print(
        f"IK All: ok={ok_ik_all}, solutions={len(all_solutions)}, "
        f"error={getattr(all_result, 'kinematic_error', 'UNKNOWN')}"
    )

    if all_solutions:
        _print_vec("IK All Solution[0]", all_solutions[0])

    print("[INFO] Kinematics example finished successfully")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as ex:
        print(f"[ERROR] Unexpected exception: {ex}", file=sys.stderr)
        sys.exit(1)
