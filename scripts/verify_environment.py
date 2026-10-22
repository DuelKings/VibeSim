#!/usr/bin/env python3
import argparse, json, os, shutil, subprocess, sys
from pathlib import Path


def resolve(value):
    if not value or str(value).startswith("REPLACE"):
        return None
    value = os.path.expanduser(str(value))
    return shutil.which(value) or (value if Path(value).exists() else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    failures = []
    report = {"config": str(Path(args.config).resolve()), "executables": {}, "paths": {}}
    for name, configured in cfg.get("executables", {}).items():
        found = resolve(configured)
        report["executables"][name] = {"configured": configured, "resolved": found}
        if not found:
            failures.append(f"missing executable: {name}")
    for key in ("shared_artifact_dir_linux", "linux_scratch_dir", "pseudopotential_root"):
        value = cfg.get(key)
        ok = bool(value and not str(value).startswith("REPLACE") and Path(os.path.expanduser(str(value))).exists())
        report["paths"][key] = {"configured": value, "exists": ok}
        if not ok:
            failures.append(f"missing/unconfigured path: {key}")
    limits = cfg.get("limits", {})
    if limits.get("minimum_available_ram_gib", 0) < 4:
        failures.append("minimum_available_ram_gib must be at least 4")
    report["limits"] = limits
    report["ok"] = not failures
    report["failures"] = failures
    print(json.dumps(report, indent=2))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
