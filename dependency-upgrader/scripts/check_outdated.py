#!/usr/bin/env python3
"""check_outdated.py - Auto-detect the package ecosystem in a repo and report
outdated dependencies grouped by semver risk tier (patch / minor / major).

Pure standard library. Shells out to the native package manager to gather data
(e.g. `npm outdated --json`, `pip list --outdated --json`, `cargo outdated`).

Usage:
    python3 check_outdated.py [--dir PATH] [--json]

Options:
    --dir PATH   Repository directory to inspect (default: current directory).
    --json       Emit machine-readable JSON instead of the human table.

Exit codes:
    0  ran successfully (regardless of whether updates were found)
    2  no supported ecosystem detected, or the native tool is unavailable
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys


def run(cmd, cwd):
    """Run a command, returning (returncode, stdout, stderr). Never raises."""
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=180
        )
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError:
        return 127, "", f"command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", f"timed out: {' '.join(cmd)}"


def parse_version(v):
    """Return (major, minor, patch) ints from a version string, best effort."""
    if not v:
        return None
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", v)
    if not m:
        m = re.search(r"(\d+)\.(\d+)", v)
        if m:
            return (int(m.group(1)), int(m.group(2)), 0)
        m = re.search(r"(\d+)", v)
        return (int(m.group(1)), 0, 0) if m else None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def classify(current, latest):
    """Risk tier from current -> latest. 0.x minor is treated as major."""
    c, l = parse_version(current), parse_version(latest)
    if not c or not l:
        return "unknown"
    if l <= c:
        return "none"
    if l[0] != c[0]:
        return "major"
    # same major: 0.x lines treat minor bumps as breaking
    if c[0] == 0 and l[1] != c[1]:
        return "major"
    if l[1] != c[1]:
        return "minor"
    return "patch"


def detect(repo):
    """Return the ecosystem name based on manifest files present."""
    exists = lambda f: os.path.exists(os.path.join(repo, f))
    if exists("package.json"):
        if exists("pnpm-lock.yaml"):
            return "pnpm"
        if exists("yarn.lock"):
            return "yarn"
        return "npm"
    if exists("Cargo.toml"):
        return "cargo"
    if exists("go.mod"):
        return "go"
    if exists("poetry.lock") or exists("pyproject.toml"):
        return "python"
    if any(exists(f) for f in ("requirements.txt", "requirements-dev.txt")):
        return "python"
    return None


def collect_npm(repo, binary):
    code, out, _ = run([binary, "outdated", "--json"], repo)
    # npm exits 1 when outdated packages exist; that is expected.
    if not out.strip():
        return []
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return []
    rows = []
    for name, info in data.items():
        cur = info.get("current") or info.get("wanted")
        latest = info.get("latest")
        rows.append({"name": name, "current": cur, "latest": latest,
                     "tier": classify(cur, latest)})
    return rows


def collect_python(repo):
    code, out, _ = run([sys.executable, "-m", "pip", "list",
                        "--outdated", "--format=json"], repo)
    if code not in (0,) or not out.strip():
        return []
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return []
    rows = []
    for item in data:
        cur, latest = item.get("version"), item.get("latest_version")
        rows.append({"name": item.get("name"), "current": cur,
                     "latest": latest, "tier": classify(cur, latest)})
    return rows


def collect_cargo(repo):
    # cargo-outdated emits a text table; parse defensively.
    code, out, err = run(["cargo", "outdated", "--format", "json"], repo)
    rows = []
    if code == 0 and out.strip():
        try:
            data = json.loads(out)
            for dep in data.get("dependencies", []):
                cur, latest = dep.get("project"), dep.get("latest")
                rows.append({"name": dep.get("name"), "current": cur,
                             "latest": latest, "tier": classify(cur, latest)})
            return rows
        except json.JSONDecodeError:
            pass
    return rows


def collect_go(repo):
    code, out, _ = run(["go", "list", "-m", "-u", "-f",
                        "{{.Path}} {{.Version}} {{if .Update}}{{.Update.Version}}{{end}}",
                        "all"], repo)
    rows = []
    if code != 0:
        return rows
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 3:
            name, cur, latest = parts
            rows.append({"name": name, "current": cur, "latest": latest,
                         "tier": classify(cur, latest)})
    return rows


def gather(repo, eco):
    if eco in ("npm", "yarn", "pnpm"):
        binary = "npm" if eco == "npm" else eco
        if not shutil.which(binary):
            binary = "npm"  # npm outdated works regardless of lockfile manager
        if not shutil.which(binary):
            return None
        return collect_npm(repo, binary)
    if eco == "python":
        return collect_python(repo)
    if eco == "cargo":
        if not shutil.which("cargo"):
            return None
        return collect_cargo(repo)
    if eco == "go":
        if not shutil.which("go"):
            return None
        return collect_go(repo)
    return None


TIER_ORDER = {"major": 0, "minor": 1, "patch": 2, "unknown": 3, "none": 4}


def print_table(eco, rows):
    actionable = [r for r in rows if r["tier"] not in ("none",)]
    actionable.sort(key=lambda r: (TIER_ORDER.get(r["tier"], 5), r["name"]))
    print(f"Ecosystem detected: {eco}")
    if not actionable:
        print("All dependencies are up to date.")
        return
    print(f"{len(actionable)} outdated package(s):\n")
    width = max((len(r["name"]) for r in actionable), default=4)
    header = f"{'PACKAGE':<{width}}  {'CURRENT':<12} {'LATEST':<12} TIER"
    print(header)
    print("-" * len(header))
    for r in actionable:
        flag = "  <-- isolate" if r["tier"] == "major" else ""
        print(f"{r['name']:<{width}}  {str(r['current']):<12} "
              f"{str(r['latest']):<12} {r['tier']}{flag}")
    majors = sum(1 for r in actionable if r["tier"] == "major")
    print(f"\nSummary: {majors} major (isolate, one commit each), "
          f"{sum(1 for r in actionable if r['tier'] == 'minor')} minor, "
          f"{sum(1 for r in actionable if r['tier'] == 'patch')} patch.")
    print("Tip: batch patch+minor, isolate every major. See SKILL.md workflow.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default=".", help="repository directory")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args(argv)

    repo = os.path.abspath(args.dir)
    if not os.path.isdir(repo):
        print(f"error: not a directory: {repo}", file=sys.stderr)
        return 2

    eco = detect(repo)
    if not eco:
        print("error: no supported ecosystem detected (looked for "
              "package.json, Cargo.toml, go.mod, pyproject.toml, "
              "requirements.txt)", file=sys.stderr)
        return 2

    rows = gather(repo, eco)
    if rows is None:
        print(f"error: native tooling for '{eco}' is unavailable on PATH",
              file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({"ecosystem": eco, "packages": rows}, indent=2))
    else:
        print_table(eco, rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
